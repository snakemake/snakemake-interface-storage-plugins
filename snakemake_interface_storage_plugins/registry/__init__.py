__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

import types
from typing import List, Mapping

from snakemake_interface_storage_plugins.settings import (
    StorageProviderSettingsBase,
)
from snakemake_interface_common.plugin_registry.attribute_types import (
    AttributeKind,
    AttributeMode,
    AttributeType,
)
from snakemake_interface_storage_plugins.registry.plugin import Plugin
from snakemake_interface_common.plugin_registry import PluginRegistryBase
from snakemake_interface_storage_plugins import common
from snakemake_interface_storage_plugins.storage_provider import StorageProviderBase


class StoragePluginRegistry(PluginRegistryBase):
    """This class is a singleton that holds all registered executor plugins."""

    def get_registered_read_write_plugins(self) -> List[str]:
        return [
            plugin.name
            for plugin in self.plugins.values()
            if plugin.storage_provider.is_read_write
        ]

    @property
    def module_prefix(self) -> str:
        return common.storage_plugin_module_prefix

    def load_plugin(self, name: str, module: types.ModuleType) -> Plugin:
        """Load a plugin by name."""
        return Plugin(
            _name=name,
            storage_provider=module.StorageProvider,
            _storage_settings_cls=getattr(module, "StorageProviderSettings", None),
        )

    def expected_attributes(self) -> Mapping[str, AttributeType]:
        return {
            "StorageSettings": AttributeType(
                cls=StorageProviderSettingsBase,
                mode=AttributeMode.OPTIONAL,
                kind=AttributeKind.CLASS,
            ),
            "StorageProvider": AttributeType(
                cls=StorageProviderBase,
                mode=AttributeMode.REQUIRED,
                kind=AttributeKind.CLASS,
            ),
        }
