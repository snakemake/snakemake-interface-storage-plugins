__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from typing import List, Optional, Type
from snakemake_interface_storage_plugins.io import get_constant_prefix
from snakemake_interface_storage_plugins.registry import StoragePluginRegistry
from snakemake_interface_common.plugin_registry.tests import TestRegistryBase
from snakemake_interface_common.plugin_registry.plugin import PluginBase, SettingsBase
from snakemake_interface_common.plugin_registry import PluginRegistryBase
from snakemake_interface_storage_plugins.settings import StorageProviderSettingsBase

from snakemake_interface_storage_plugins.storage_provider import StorageProviderBase

from snakemake_storage_plugin_http import StorageProvider, StorageProviderSettings

from snakemake_interface_storage_plugins.tests import TestStorageBase


class TestRegistry(TestRegistryBase):
    __test__ = True

    def get_registry(self) -> PluginRegistryBase:
        # ensure that the singleton is reset
        StoragePluginRegistry._instance = None
        return StoragePluginRegistry()

    def get_test_plugin_name(self) -> str:
        return "http"

    def validate_plugin(self, plugin: PluginBase):
        assert plugin._storage_settings_cls is not None
        assert plugin.storage_provider is not None
        assert not plugin.is_read_write()

    def validate_settings(self, settings: SettingsBase, plugin: PluginBase):
        assert isinstance(settings, plugin._storage_settings_cls)

    def get_example_args(self):
        return []


class TestTestStorageBase(TestStorageBase):
    __test__ = True
    retrieve_only = True

    def get_query(self, tmp_path) -> str:
        return "https://www.google.com"

    def get_query_not_existing(self, tmp_path) -> str:
        return "https://www.google.com/this/does/not/exist"

    def get_storage_provider_cls(self) -> Type[StorageProviderBase]:
        return StorageProvider

    def get_storage_provider_settings(self) -> Optional[StorageProviderSettingsBase]:
        return StorageProviderSettings()

    def get_example_args(self) -> List[str]:
        return []


def test_get_constant_prefix():
    assert get_constant_prefix("foo/bar/{wildcard}/baz") == "foo/bar/"
    assert (
        get_constant_prefix("foo/bar/{wildcard}/baz", strip_incomplete_parts=True)
        == "foo/bar/"
    )
    assert (
        get_constant_prefix("foo/bar{wildcard}/baz/", strip_incomplete_parts=True)
        == "foo/"
    )
    assert (
        get_constant_prefix("foo/bar{wildcard}/baz", strip_incomplete_parts=False)
        == "foo/bar"
    )
    assert (
        get_constant_prefix(
            "{wildcard}/foo/bar/{wildcard}/baz", strip_incomplete_parts=True
        )
        == ""
    )
    assert (
        get_constant_prefix(
            "{wildcard}/foo/bar/{wildcard}/baz", strip_incomplete_parts=False
        )
        == ""
    )
