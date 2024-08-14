__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from abc import ABC, abstractmethod
import asyncio
from pathlib import Path
import shutil
import sys
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
    touch = False
    files_only = True

    @abstractmethod
    def get_storage_provider_cls(self) -> Type[StorageProviderBase]: ...

    def get_storage_provider_settings(self) -> Optional[StorageProviderSettingsBase]:
        return None

    @abstractmethod
    def get_query(self, tmp_path) -> str: ...

    @abstractmethod
    def get_query_not_existing(self, tmp_path) -> str: ...

    def _get_obj(self, tmp_path, query):
        provider = self._get_provider(tmp_path)

        return provider.object(query)

    def test_storage(self, tmp_path):
        self._test_storage(tmp_path, directory=False)
        if not self.files_only:
            self._test_storage(tmp_path, directory=True)

    def _test_storage(self, tmp_path, directory=False):
        print(
            f"Testing storage of {'files' if not directory else 'directories'}.",
            file=sys.stderr,
        )

        assert not (
            self.store_only and self.retrieve_only
        ), "store_only and retrieve_only may not be True at the same time"

        obj = self._get_obj(tmp_path, self.get_query(tmp_path))

        stored = False

        if directory:
            dirpath = obj.local_path()
            filepath = dirpath / "test.txt"
        else:
            dirpath = obj.local_path().parent
            filepath = obj.local_path()

        try:
            if not self.retrieve_only:
                if dirpath.exists():
                    if dirpath.is_dir():
                        shutil.rmtree(dirpath)
                    else:
                        dirpath.unlink()
                dirpath.mkdir(parents=True, exist_ok=True)
                with open(filepath, "w") as f:
                    f.write("test")
                    f.flush()
                obj.store_object()
                stored = True
                if directory:
                    shutil.rmtree(dirpath)
                else:
                    filepath.unlink()

            assert obj.exists()

            assert isinstance(obj.mtime(), (float, int))

            self._test_inventory(obj)

            if self.touch:
                obj.touch()

            if not self.store_only:
                dirpath.mkdir(parents=True, exist_ok=True)
                obj.retrieve_object()
                assert filepath.exists()

        finally:
            if not self.retrieve_only and stored and self.delete:
                obj.remove()

    def test_storage_not_existing(self, tmp_path):
        obj = self._get_obj(tmp_path, self.get_query_not_existing(tmp_path))

        assert not obj.exists()

    def _test_inventory(self, obj):
        cache = IOCache(max_wait_time=10)
        # create inventory entry if implemented in StorageObject
        asyncio.run(obj.inventory(cache))
        # Check whether second run of inventory passes (should not perform any action
        # though)
        # TODO: Mock the cache to make sure that no second storing happens
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

    def test_example_queries(self, tmp_path):
        provider = self._get_provider(tmp_path)
        queries = provider.example_queries()
        assert isinstance(queries, list)
        assert len(queries) > 0
