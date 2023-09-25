__author__ = "Christopher Tomkins-Tinch"
__copyright__ = "Copyright 2022, Christopher Tomkins-Tinch"
__email__ = "tomkinsc@broadinstitute.org"
__license__ = "MIT"


from dataclasses import dataclass
import os
from pathlib import Path
import sys
from abc import ABC, abstractmethod
from typing import Any, Optional, Sequence, Set
from snakemake_interface_storage_plugins.io import (
    MaybeAnnotated,
    flag,
    glob_wildcards,
    is_flagged,
)
from snakemake_interface_storage_plugins.settings import StorageProviderSettingsBase

from snakemake_interface_storage_plugins.storage_object import StaticStorageObjectProxy


@dataclass
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
        stay_on_remote=False,
        is_default=False,
    ):
        self.local_prefix = local_prefix
        self.settings = settings
        self.stay_on_remote = stay_on_remote
        self.keep_local = keep_local
        self.is_default = is_default

    def object(
        self,
        query: Any,
        keep_local: Optional[bool]=None, 
        retrieve: bool=True, 
        static: bool=False,
    ):
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

    @abstractmethod
    def default_protocol(self) -> str:
        """The protocol that is prepended to the path when no protocol is specified."""
        ...

    @abstractmethod
    def available_protocols(self) -> Sequence[str]:
        """List of valid protocols for this remote provider."""
        ...
