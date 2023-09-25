from abc import ABC, abstractmethod
import os
from typing import Any, Optional
from snakemake_interface_storage_plugins.settings import StorageProviderSettingsBase

from snakemake_interface_storage_plugins.storage_provider import StorageProviderBase


class TestStorageBase(ABC):
    __test__ = False
    retrieve_only = False

    @abstractmethod
    def get_storage_provider(self) -> StorageProviderBase:
        ...

    @abstractmethod
    def get_query(self) -> Any:
        ...

    @abstractmethod
    def get_storage_settings(self) -> Optional[StorageProviderSettingsBase]:
        ...

    def test_storage(self, tmp_path):
        orig_path = os.getcwd()
        os.chdir(tmp_path)
        try:
            provider = self.get_storage_provider(self.get_storage_settings())

            obj = provider.object(self.get_query())

            if not self.retrieve_only:
                with open(obj.local_path(), "w") as f:
                    f.write("test")
                obj.upload()

            assert obj.exists()
            print(obj.mtime())
            print(obj.size())

            obj.download()
        finally:
            os.chdir(orig_path)
