__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

import os
from abc import ABC, abstractmethod
import shutil
from typing import Iterable, Optional

from wrapt import ObjectProxy
from reretry import retry
import copy

from snakemake_interface_common.exceptions import WorkflowError
from snakemake_interface_common.logging import get_logger

from snakemake_interface_storage_plugins.io import IOCacheStorageInterface
from snakemake_interface_storage_plugins.storage_provider import StorageProviderBase


retry_decorator = retry(tries=3, delay=3, backoff=2, logger=get_logger())


class StaticStorageObjectProxy(ObjectProxy):
    """Proxy that implements static-ness for remote objects.

    The constructor takes a real RemoteObject and returns a proxy that
    behaves the same except for the exists() and mtime() methods.

    """

    def exists(self):
        return True

    def mtime(self) -> float:
        return float("-inf")

    def is_newer(self, time):
        return False

    def __copy__(self):
        copied_wrapped = copy.copy(self.__wrapped__)
        return type(self)(copied_wrapped)

    def __deepcopy__(self, memo):
        copied_wrapped = copy.deepcopy(self.__wrapped__, memo)
        return type(self)(copied_wrapped)


class StorageObjectBase(ABC):
    """This is an abstract class to be used to derive storage object classes for
    different cloud storage providers. For example, there could be classes for
    interacting with Amazon AWS S3 and Google Cloud Storage, both derived from this
    common base class.
    """

    def __init__(
        self,
        query: str,
        keep_local: bool,
        retrieve: bool,
        provider: StorageProviderBase,
    ):
        self.query = query
        self.keep_local = keep_local
        self.retrieve = retrieve
        self.provider = provider
        self.__post_init__()

    def __post_init__(self):  # noqa B027
        pass

    def is_valid_query(self) -> bool:
        """Return True is the query is valid for this storage provider."""
        return self.provider.is_valid_query(self.query)

    def local_path(self):
        """Return the local path that would represent the query."""
        return self.provider.local_prefix / self.local_suffix()

    @abstractmethod
    def local_suffix(self):
        """Return a unique suffix for the local path of the object."""
        # This can be a hexdigest of the query, or ideally a meaningful name.
        # For example, if the query is a URL, it can be the URL without the protocol
        # part and any optional parameters if that does not hamper the uniqueness.
        ...


class StorageObjectRead(StorageObjectBase):
    @abstractmethod
    async def inventory(self, cache: IOCacheStorageInterface):
        """From this file, try to find as much existence and modification date
        information as possible.
        """
        # If this is implemented in a remote object, results have to be stored in
        # the given IOCache object.
        ...

    @abstractmethod
    def get_inventory_parent(self) -> Optional[str]:
        ...

    @abstractmethod
    def close(self):
        ...

    @abstractmethod
    def exists(self) -> bool:
        ...

    @abstractmethod
    def mtime(self) -> float:
        ...

    @abstractmethod
    def size(self) -> int:
        ...

    @abstractmethod
    def retrieve_object(self):
        ...

    def managed_retrieve(self):
        self.local_path().parent.mkdir(parents=True, exist_ok=True)
        try:
            return self.retrieve_object()
        except Exception as e:
            # clean up potentially partially downloaded data
            local_path = self.local_path()
            if os.path.exists(local_path):
                if os.path.isdir(local_path):
                    shutil.rmtree(local_path)
                else:
                    os.remove(local_path)
            raise WorkflowError(
                f"Failed to retrieve storage object from {self.query}", e
            )


class StorageObjectWrite(StorageObjectBase):
    @abstractmethod
    def store_object(self):
        ...

    @abstractmethod
    def remove(self):
        ...

    def managed_store(self):
        try:
            self.store_object()
        except Exception as e:
            raise WorkflowError(f"Failed to store output in storage {self.query}", e)


class StorageObjectGlob(StorageObjectBase):
    @abstractmethod
    def list_candidate_matches(self) -> Iterable[str]:
        """Return a list of candidate matches in the storage for the query."""
        # This is used by glob_wildcards() to find matches for wildcards in the query.
        # The method has to return concretized queries without any remaining wildcards.
        ...
