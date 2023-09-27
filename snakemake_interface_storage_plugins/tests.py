__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, Type

from snakemake_interface_storage_plugins.storage_provider import StorageProviderBase
from snakemake_interface_storage_plugins.settings import (
    StorageProviderSettingsBase,
)


class TestStorageBase(ABC):
    __test__ = False
    retrieve_only = False

    @abstractmethod
    def get_storage_provider_cls(self) -> Type[StorageProviderBase]:
        ...

    def get_storage_provider_settings(self) -> Optional[StorageProviderSettingsBase]:
        return None

    @abstractmethod
    def get_query(self) -> Any:
        ...

    def test_storage(self, tmp_path):
        provider = self.get_storage_provider_cls()(
            local_prefix=Path(tmp_path),
            settings=self.get_storage_provider_settings(),
        )

        obj = provider.object(self.get_query())
        obj = obj.flags["storage_object"]

        stored = False
        try:
            if not self.retrieve_only:
                obj.local_path().parent.mkdir(parents=True, exist_ok=True)
                with open(obj.local_path(), "w") as f:
                    f.write("test")
                    f.flush()
                obj.managed_store()
                stored = True
                obj.local_path().unlink()

            assert obj.exists()
            print(obj.mtime())
            print(obj.size())

            obj.managed_retrieve()

        finally:
            if not self.retrieve_only and stored:
                obj.remove()
