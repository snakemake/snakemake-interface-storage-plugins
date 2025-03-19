__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"


from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from logging import Logger
from pathlib import Path
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, AsyncGenerator, TypeVar

from throttler import Throttler
from snakemake_interface_common.exceptions import WorkflowError
from snakemake_interface_storage_plugins.common import Operation
from snakemake_interface_storage_plugins.settings import StorageProviderSettingsBase


@dataclass
class StorageQueryValidationResult:
    """Result of validating a storage query string.

    Represents whether a query string is valid for a storage provider
    and provides a reason if the validation fails.

    Parameters
    ----------
    query : str
        The query string being validated.
    valid : bool
        Whether the query is valid for the storage provider.
    reason : str, optional
        If invalid, explanation of why validation failed.
    """

    query: str
    valid: bool
    reason: Optional[str] = None

    def __str__(self) -> str:
        if self.valid:
            return f"query {self.query} is valid"
        elif self.reason:
            return f"query {self.query} is invalid: {self.reason}"
        else:
            return f"query {self.query} is invalid. Reason Unknown"

    def __bool__(self) -> bool:
        return self.valid


class QueryType(Enum):
    """Enumeration of query types for storage providers.

    Defines the context in which a query will be used within a workflow.

    Attributes
    ----------
    INPUT : int
        Query used for reading/retrieving data from storage.
    OUTPUT : int
        Query used for writing/storing data to storage.
    ANY : int
        Query usable for both input and output operations.
    """

    INPUT = 0
    OUTPUT = 1
    ANY = 2


@dataclass
class ExampleQuery:
    """Example query for a storage provider with description and intended usage.

    Provides documentation and examples for users to understand how to construct
    valid queries for a specific storage provider.

    Parameters
    ----------
    query : str
        Example query string demonstrating correct format.
    description : str
        Human-readable explanation of what the query does.
    type : QueryType
        Whether this example is for input, output, or both.
    """

    query: str
    description: str
    type: QueryType


TStorageProviderSettings = TypeVar(
    "TStorageProviderSettings",
    bound="StorageProviderSettingsBase",
    default=StorageProviderSettingsBase,
)


class StorageProviderBase(ABC, Generic[TStorageProviderSettings]):
    """Abstract base class for Snakemake storage providers.

    Defines the interface for interacting with external storage systems
    like S3, GCS, HTTP, etc. Storage providers handle authentication,
    rate limiting, caching, and mapping between remote resources and
    local files within Snakemake workflows.

    Parameters
    ----------
    local_prefix : Path
        Directory where remote files are cached locally.
    settings : StorageProviderSettingsBase, optional
        Provider-specific configuration options.
    keep_local : bool, default=False
        Whether to retain local copies after workflow completion.
    retrieve : bool, default=True
        Whether to automatically fetch remote files when referenced.
    is_default : bool, default=False
        Whether this provider is the default for its protocol.
    """

    # Class attributes with type hints
    local_prefix: Path
    settings: Optional[StorageProviderSettingsBase]
    keep_local: bool
    retrieve: bool
    is_default: bool
    _rate_limiters: Dict[Any, Throttler]

    def __init__(
        self,
        local_prefix: Path,
        logger: Logger,
        wait_for_free_local_storage: Optional[int] = None,
        settings: Optional[StorageProviderSettingsBase] = None,
        keep_local: bool = False,
        retrieve: bool = True,
        is_default: bool = False,
    ):
        self.logger: Logger = logger
        self.wait_for_free_local_storage: int = wait_for_free_local_storage
        try:
            local_prefix.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise WorkflowError(
                f"Failed to create local storage prefix {local_prefix}", e
            )
        self.local_prefix = local_prefix
        self.settings = settings
        self.keep_local = keep_local
        self.retrieve = retrieve
        self.is_default = is_default
        self._rate_limiters = dict()
        try:
            self.local_prefix.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise WorkflowError(
                f"Failed to create local storage prefix {self.local_prefix}", e
            )
        self.__post_init__()

    def __post_init__(self) -> None:
        """Hook for subclasses to perform additional initialization.

        Subclasses may override this method to perform additional setup
        after the base class has been initialized.
        """
        pass

    def rate_limiter(self, query: str, operation: Operation) -> Throttler:
        if not self.use_rate_limiter():
            return self._noop_context()
        else:
            key = self.rate_limiter_key(query, operation)
            if key not in self._rate_limiters:
                max_status_checks_frac = Fraction(
                    (self.settings.max_requests_per_second if self.settings else None)
                    or self.default_max_requests_per_second()
                ).limit_denominator()
                self._rate_limiters[key] = Throttler(
                    rate_limit=max_status_checks_frac.numerator,
                    period=max_status_checks_frac.denominator,
                )
            return self._rate_limiters[key]

    @asynccontextmanager
    async def _noop_context(self) -> AsyncGenerator[Any, Any]:
        yield

    @classmethod
    @abstractmethod
    def example_queries(cls) -> List[ExampleQuery]:
        """Return a example queries with description for this storage provider."""
        ...

    @abstractmethod
    def rate_limiter_key(self, query: str, operation: Operation) -> Any:
        """Return a key for identifying a rate limiter given a query and an operation.

        This is used to identify a rate limiter for the query.
        E.g. for a storage provider like http that would be the host name.
        For s3 it might be just the endpoint URL.
        """
        ...

    @abstractmethod
    def default_max_requests_per_second(self) -> float:
        """Return the default maximum number of requests per second for this storage
        provider."""
        ...

    @abstractmethod
    def use_rate_limiter(self) -> bool:
        """Return False if no rate limiting is needed for this provider."""
        ...

    @classmethod
    @abstractmethod
    def is_valid_query(cls, query: str) -> StorageQueryValidationResult:
        """Validate the given query for this storage provider.

        This should also work when the query contains wildcards (e.g. "{sample}").
        """
        ...

    def postprocess_query(self, query: str) -> str:
        """Postprocess the query to make it suitable and as informative as possible.

        This can e.g. be modified in a subclass to add a protocol or global settings,
        or normalize the scheme if multiple ones are possible.
        """
        return query

    def safe_print(self, query: str) -> str:
        """Process the query to remove potentially sensitive information when printing.

        Useful if the query is URL-like and can contain authentication tokens in the
        parameters and/or usernames/passwords.
        """
        return query

    @property
    def is_read_write(self) -> bool:
        from snakemake_interface_storage_plugins.storage_object import (
            StorageObjectRead,
            StorageObjectWrite,
        )

        cls = self.get_storage_object_cls()
        return issubclass(cls, StorageObjectRead) and issubclass(
            cls, StorageObjectWrite
        )

    @classmethod
    def get_storage_object_cls(cls) -> type:
        provider = sys.modules[cls.__module__]  # get module of derived class
        return provider.StorageObject

    def object(
        self,
        query: str,
        keep_local: Optional[bool] = None,
        retrieve: Optional[bool] = None,
        static: bool = False,
    ) -> Any:
        from snakemake_interface_storage_plugins.storage_object import (
            StaticStorageObjectProxy,
        )

        query = self.postprocess_query(query)

        if keep_local is None:
            keep_local = self.keep_local

        if retrieve is None:
            retrieve = self.retrieve

        storage_object = self.get_storage_object_cls()(
            query=query,
            keep_local=keep_local,
            retrieve=retrieve,
            provider=self,
        )

        if static:
            storage_object = StaticStorageObjectProxy(storage_object)

        return storage_object
