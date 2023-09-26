__author__ = "Johannes Köster"
__copyright__ = "Copyright 2022, Johannes Köster, Vanessa Sochat"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

import types
from typing import Mapping
from snakemake_interface_storage_plugins.settings import (
    StorageSettingsBase,
)

from snakemake_interface_common.plugin_registry.attribute_types import (
    AttributeKind,
    AttributeMode,
    AttributeType,
)
from snakemake_interface_storage_plugins.registry.plugin import Plugin
from snakemake_interface_common.plugin_registry import PluginRegistryBase
from snakemake_interface_storage_plugins import _common as common
from snakemake_interface_storage_plugins.storage_provider import StorageProviderBase


class StoragePluginRegistry(PluginRegistryBase):
    """This class is a singleton that holds all registered executor plugins."""

    @property
    def module_prefix(self) -> str:
        return common.executor_plugin_module_prefix

    def load_plugin(self, name: str, module: types.ModuleType) -> Plugin:
        """Load a plugin by name."""
        return Plugin(
            _name=name,
            storage_provider=module.StorageProvider,
            _storage_settings_cls=getattr(module, "StorageSettings", None),
        )

    def expected_attributes(self) -> Mapping[str, AttributeType]:
        return {
            "StorageSettings": AttributeType(
                cls=StorageSettingsBase,
                mode=AttributeMode.OPTIONAL,
                kind=AttributeKind.CLASS,
            ),
            "StorageProvider": AttributeType(
                cls=StorageProviderBase,
                mode=AttributeMode.REQUIRED,
                kind=AttributeKind.CLASS,
            ),
        }
