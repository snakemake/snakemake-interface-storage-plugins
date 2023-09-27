__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"


from dataclasses import dataclass
from pathlib import Path
import sys
from abc import ABC, abstractmethod
from typing import Iterable, Optional
from snakemake_interface_storage_plugins.io import (
    flag,
)
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


class StorageProviderBase(ABC):
    """This is an abstract class to be used to derive remote provider classes.
    These might be used to hold common credentials,
    and are then passed to StorageObjects.
    """

    supports_default = False

    def __init__(
        self,
        local_prefix: Path,
        settings: Optional[StorageProviderSettingsBase] = None,
        keep_local=False,
        is_default=False,
    ):
        self.local_prefix = local_prefix
        self.settings = settings
        self.keep_local = keep_local
        self.is_default = is_default
        self.__post_init__()

    def __post_init__(self):  # noqa B027
        pass

    @classmethod
    @abstractmethod
    def is_valid_query(cls, query: str) -> StorageQueryValidationResult:
        """Validate the given query for this storage provider.

        This should also work when the query contains wildcards (e.g. "{sample}").
        """
        ...

    @property
    def is_read_write(self) -> bool:
        from snakemake_interface_storage_plugins.storage_object import (
            StorageObjectReadWrite,
        )

        return isinstance(self.storage_object_cls, StorageObjectReadWrite)

    @property
    def storage_object_cls(self):
        provider = sys.modules[self.__module__]  # get module of derived class
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

        if keep_local is None:
            keep_local = self.keep_local

        storage_object = self.storage_object_cls(
            query=query,
            keep_local=keep_local,
            retrieve=retrieve,
            provider=self,
        )

        if static:
            storage_object = StaticStorageObjectProxy(storage_object)

        return flag(storage_object.local_path(), "storage_object", storage_object)

    @abstractmethod
    def list_objects(self, query: str) -> Iterable[str]:
        """Return an iterator over all objects in the storage that match the query.

        This is optional and can raise a NotImplementedError() instead.
        """
        ...
