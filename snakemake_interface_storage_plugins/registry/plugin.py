__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from dataclasses import dataclass
from typing import Optional, Type
from snakemake_interface_storage_plugins.settings import (
    StorageProviderSettingsBase,
)
from snakemake_interface_storage_plugins import common

from snakemake_interface_common.plugin_registry.plugin import PluginBase


@dataclass
class Plugin(PluginBase):
    storage_provider: object
    _storage_settings_cls: Optional[Type[StorageProviderSettingsBase]]
    _name: str

    @property
    def support_tagged_values(self) -> bool:
        return True

    @property
    def name(self):
        return self._name

    @property
    def cli_prefix(self):
        return "storage-" + self.name.replace(common.storage_plugin_module_prefix, "")

    @property
    def settings_cls(self):
        return self._storage_settings_cls
