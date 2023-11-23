__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from abc import ABC, abstractmethod
import asyncio
from pathlib import Path
from typing import Optional, Type

from snakemake_interface_storage_plugins.storage_provider import (
    StorageProviderBase,
    StorageQueryValidationResult,
)
from snakemake_interface_storage_plugins.settings import (
    StorageProviderSettingsBase,
)
from snakemake.io import IOCache


class TestStorageBase(ABC):
    __test__ = False
    retrieve_only = False
    store_only = False
    delete = True

    @abstractmethod
    def get_storage_provider_cls(self) -> Type[StorageProviderBase]:
        ...

    def get_storage_provider_settings(self) -> Optional[StorageProviderSettingsBase]:
        return None

    @abstractmethod
    def get_query(self, tmp_path) -> str:
        ...

    @abstractmethod
    def get_query_not_existing(self, tmp_path) -> str:
        ...

    def _get_obj(self, tmp_path, query):
        provider = self._get_provider(tmp_path)

        return provider.object(query)

    def test_storage(self, tmp_path):
        assert not (
            self.store_only and self.retrieve_only
        ), "store_only and retrieve_only may not be True at the same time"

        obj = self._get_obj(tmp_path, self.get_query(tmp_path))

        stored = False
        try:
            if not self.retrieve_only:
                obj.local_path().parent.mkdir(parents=True, exist_ok=True)
                with open(obj.local_path(), "w") as f:
                    f.write("test")
                    f.flush()
                obj.store_object()
                stored = True
                obj.local_path().unlink()

            assert obj.exists()
            print(obj.mtime())
            print(obj.size())

            if not self.store_only:
                obj.local_path().parent.mkdir(parents=True, exist_ok=True)
                obj.retrieve_object()

        finally:
            if not self.retrieve_only and stored and self.delete:
                obj.remove()

    def test_storage_not_existing(self, tmp_path):
        obj = self._get_obj(tmp_path, self.get_query_not_existing(tmp_path))

        assert not obj.exists()

    def test_inventory(self, tmp_path):
        obj = self._get_obj(tmp_path, self.get_query(tmp_path))
        cache = IOCache(max_wait_time=10)
        asyncio.run(obj.inventory(cache))

    def test_query_validation(self, tmp_path):
        provider = self._get_provider(tmp_path)
        res = provider.is_valid_query(self.get_query(tmp_path))
        assert isinstance(res, StorageQueryValidationResult)
        assert res

    def _get_provider(self, tmp_path):
        return self.get_storage_provider_cls()(
            local_prefix=Path(tmp_path) / "local_prefix",
            settings=self.get_storage_provider_settings(),
        )
