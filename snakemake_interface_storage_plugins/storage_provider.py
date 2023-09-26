__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"


from pathlib import Path
import sys
from abc import ABC
from typing import Any, Optional
from snakemake_interface_storage_plugins.io import (
    flag,
)
from snakemake_interface_storage_plugins.settings import StorageProviderSettingsBase


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

    def object(
        self,
        query: Any,
        keep_local: Optional[bool] = None,
        retrieve: bool = True,
        static: bool = False,
    ):
        from snakemake_interface_storage_plugins.storage_object import (
            StaticStorageObjectProxy,
        )

        if keep_local is None:
            keep_local = self.keep_local

        provider = sys.modules[self.__module__]  # get module of derived class
        storage_object = provider.StorageObject(
            query=query,
            keep_local=keep_local,
            retrieve=retrieve,
            provider=self,
        )

        if static:
            storage_object = StaticStorageObjectProxy(storage_object)

        return flag(storage_object.local_path(), "storage_object", storage_object)
