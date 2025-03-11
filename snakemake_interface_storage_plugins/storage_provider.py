__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"


from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path
import sys
from abc import ABC, abstractmethod
from typing import Any, List, Optional

from throttler import Throttler
from snakemake_interface_common.exceptions import WorkflowError
from snakemake_interface_storage_plugins.common import Operation
from snakemake_interface_storage_plugins.settings import StorageProviderSettingsBase


@dataclass
class StorageQueryValidationResult:
    query: str
    valid: bool
    reason: Optional[str] = None

    def __str__(self):
        if self.valid:
            return f"query {self.query} is valid"
        else:
            return f"query {self.query} is invalid: {self.reason}"

    def __bool__(self):
        return self.valid


class QueryType(Enum):
    INPUT = 0
    OUTPUT = 1
    ANY = 2


@dataclass
class ExampleQuery:
    query: str
    description: str
    type: QueryType


class StorageProviderBase(ABC):
    """This is an abstract class to be used to derive remote provider classes.
    These might be used to hold common credentials,
    and are then passed to StorageObjects.
    """

    def __init__(
        self,
        local_prefix: Path,
        settings: Optional[StorageProviderSettingsBase] = None,
        keep_local=False,
        is_default=False,
    ):
        try:
            local_prefix.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise WorkflowError(
                f"Failed to create local storage prefix {local_prefix}", e
            )
        self.local_prefix = local_prefix
        self.settings = settings
        self.keep_local = keep_local
        self.is_default = is_default
        self._rate_limiters = dict()
        self.__post_init__()

    def __post_init__(self):  # noqa B027
        pass

    def rate_limiter(self, query: str, operation: Operation):
        if not self.use_rate_limiter():
            return self._noop_context()
        else:
            key = self.rate_limiter_key(query, operation)
            if key not in self._rate_limiters:
                max_status_checks_frac = Fraction(
                    self.settings.max_requests_per_second
                    or self.default_max_requests_per_second()
                ).limit_denominator()
                self._rate_limiters[key] = Throttler(
                    rate_limit=max_status_checks_frac.numerator,
                    period=max_status_checks_frac.denominator,
                )
            return self._rate_limiters[key]

    @asynccontextmanager
    async def _noop_context(self):
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
            StorageObjectReadWrite,
        )

        return isinstance(self.storage_object_cls, StorageObjectReadWrite)

    @classmethod
    def get_storage_object_cls(cls):
        provider = sys.modules[cls.__module__]  # get module of derived class
        return provider.StorageObject

    def object(
        self,
        query: str,
        keep_local: Optional[bool] = None,
        retrieve: bool = True,
        static: bool = False,
    ):
        from snakemake_interface_storage_plugins.storage_object import (
            StaticStorageObjectProxy,
        )

        query = self.postprocess_query(query)

        if keep_local is None:
            keep_local = self.keep_local

        storage_object = self.get_storage_object_cls()(
            query=query,
            keep_local=keep_local,
            retrieve=retrieve,
            provider=self,
        )

        if static:
            storage_object = StaticStorageObjectProxy(storage_object)

        return storage_object
