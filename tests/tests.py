from snakemake_interface_storage_plugins.registry import StoragePluginRegistry
from snakemake_interface_common.plugin_registry.tests import TestRegistryBase
from snakemake_interface_common.plugin_registry.plugin import PluginBase, SettingsBase
from snakemake_interface_common.plugin_registry import PluginRegistryBase


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

    def validate_settings(self, settings: SettingsBase, plugin: PluginBase):
        assert isinstance(settings, plugin._storage_settings_cls)
