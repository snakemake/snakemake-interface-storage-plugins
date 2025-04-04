__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

import asyncio
import os
from abc import ABC, abstractmethod
from pathlib import Path
import shutil
from typing import Iterable, Optional

from wrapt import ObjectProxy
from reretry import retry
from humanfriendly import format_size, format_timespan
import copy

from snakemake_interface_common.exceptions import WorkflowError
from snakemake_interface_common.logging import get_logger
from snakemake_interface_storage_plugins.common import Operation, get_disk_free

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
        self.query: str = query
        self.keep_local: bool = keep_local
        self.retrieve: bool = retrieve
        self.provider: StorageProviderBase = provider
        self.print_query: str = self.provider.safe_print(self.query)
        self._overwrite_local_path: Optional[Path] = None
        self._is_ondemand_eligible: bool = False
        self.__post_init__()

    def __post_init__(self):  # noqa B027
        pass

    @property
    def is_ondemand_eligible(self) -> bool:
        return self._is_ondemand_eligible and not self.keep_local

    @is_ondemand_eligible.setter
    def is_ondemand_eligible(self, value: bool):
        self._is_ondemand_eligible = value

    def set_local_path(self, path: Path) -> None:
        """Set a custom local path for this storage object."""
        self._overwrite_local_path = path

    def is_valid_query(self) -> bool:
        """Return True is the query is valid for this storage provider."""
        return self.provider.is_valid_query(self.query)

    def local_path(self) -> Path:
        """Return the local path that would represent the query."""
        if self._overwrite_local_path:
            return self._overwrite_local_path
        else:
            return self.provider.local_prefix / self.local_suffix()

    def cache_key(self, local_suffix: Optional[str] = None) -> str:
        """Return a key for the cache."""
        assert self._overwrite_local_path is None, (
            "bug: no cache key applicable if local path is overwritten"
        )
        return str(self.provider.local_prefix / (local_suffix or self.local_suffix()))

    @abstractmethod
    def local_suffix(self) -> str:
        """Return a unique suffix for the local path of the object."""
        # This can be a hexdigest of the query, or ideally a meaningful name.
        # For example, if the query is a URL, it can be the URL without the protocol
        # part and any optional parameters if that does not hamper the uniqueness.
        ...

    def _rate_limiter(self, operation: Operation):
        return self.provider.rate_limiter(self.query, operation)


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
    def get_inventory_parent(self) -> Optional[str]: ...

    @abstractmethod
    def cleanup(self):
        """Perform local cleanup of any remainders of the storage object."""
        ...

    @abstractmethod
    def exists(self) -> bool: ...

    @abstractmethod
    def mtime(self) -> float: ...

    @abstractmethod
    def size(self) -> int:
        """Size of the object in bytes. Should return 0 for directories."""
        ...

    def local_footprint(self) -> int:
        """local footprint is the size of the object on the local disk
        For directories, this should return the recursive sum of the
        directory file sizes. Defaults to self.size() for backwards compatibility.
        """
        return self.size()

    @abstractmethod
    def retrieve_object(self):
        """Ensure that the object is accessible locally under self.local_path()

        Optionally, this can make use of the attribute self.is_ondemand_eligible,
        which indicates that the object could be retrieved on demand,
        e.g. by only symlinking or mounting it from whatever network storage this
        plugin provides. For example, objects with self.is_ondemand_eligible == True
        could mount the object via fuse instead of downloading it.
        The job can then transparently access only the parts that matter to it
        without having to wait for the full download.
        On demand eligibility is calculated via Snakemake's access pattern annotation.
        If no access pattern is annotated by the workflow developers,
        self.is_ondemand_eligible is by default set to False.
        """
        ...

    async def managed_size(self) -> int:
        try:
            async with self._rate_limiter(Operation.SIZE):
                return self.size()
        except Exception as e:
            raise WorkflowError(f"Failed to get size of {self.print_query}", e)

    async def managed_mtime(self) -> float:
        try:
            async with self._rate_limiter(Operation.MTIME):
                return self.mtime()
        except Exception as e:
            raise WorkflowError(f"Failed to get mtime of {self.print_query}", e)

    async def managed_exists(self) -> bool:
        try:
            async with self._rate_limiter(Operation.EXISTS):
                return self.exists()
        except Exception as e:
            raise WorkflowError(f"Failed to check existence of {self.print_query}", e)

    async def managed_retrieve(self):
        await self.wait_for_free_space()
        try:
            self.local_path().parent.mkdir(parents=True, exist_ok=True)
            async with self._rate_limiter(Operation.RETRIEVE):
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
                f"Failed to retrieve storage object from {self.print_query}", e
            )

    async def managed_local_footprint(self) -> int:
        try:
            async with self._rate_limiter(Operation.SIZE):
                return self.local_footprint()
        except Exception as e:
            raise WorkflowError(
                f"Failed to get expected local footprint (i.e. size) "
                f"of {self.print_query}",
                e,
            )

    async def wait_for_free_space(self):
        """Wait for free space on the disk."""
        size = await self.managed_local_footprint()
        disk_free = get_disk_free(self.local_path())

        wait_time = self.provider.wait_for_free_local_storage

        if wait_time is not None:
            if wait_time < 1:
                raise WorkflowError(
                    "Wait time for free space on local storage has to be at least "
                    "1 second or unset."
                )
            wait_time_step = 60 if wait_time > 60 else 1

            waited = 0
            while waited < wait_time and size > disk_free:
                self.provider.logger.info(
                    f"Waiting {format_timespan(wait_time_step)} for enough free "
                    f"space to store {self.local_path()} "
                    f"({format_size(size)} > {format_size(disk_free)})"
                )
                await asyncio.sleep(wait_time_step)
                waited += wait_time_step
                disk_free = get_disk_free(self.local_path())

        if size > disk_free:
            raise WorkflowError(
                f"Cannot store {self.local_path()} "
                f"({format_size(size)} > {format_size(disk_free)}), "
                f"waited {format_timespan(self.provider.wait_for_free_local_storage)} "
                "for more space."
            )


class StorageObjectWrite(StorageObjectBase):
    @abstractmethod
    def store_object(self): ...

    @abstractmethod
    def remove(self): ...

    async def managed_remove(self):
        try:
            async with self._rate_limiter(Operation.REMOVE):
                self.remove()
        except Exception as e:
            raise WorkflowError(
                f"Failed to remove storage object {self.print_query}", e
            )

    async def managed_store(self):
        try:
            async with self._rate_limiter(Operation.STORE):
                self.store_object()
        except Exception as e:
            raise WorkflowError(
                f"Failed to store output in storage {self.print_query}", e
            )


class StorageObjectGlob(StorageObjectBase):
    @abstractmethod
    def list_candidate_matches(self) -> Iterable[str]:
        """Return a list of candidate matches in the storage for the query."""
        # This is used by glob_wildcards() to find matches for wildcards in the query.
        # The method has to return concretized queries without any remaining wildcards.
        ...


class StorageObjectTouch(StorageObjectBase):
    @abstractmethod
    def touch(self):
        """Touch the object."""
        ...

    async def managed_touch(self):
        try:
            async with self._rate_limiter(Operation.TOUCH):
                self.touch()
        except Exception as e:
            raise WorkflowError(f"Failed to touch storage object {self.print_query}", e)
