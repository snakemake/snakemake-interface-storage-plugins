__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from dataclasses import dataclass
from typing import Optional, Type, TYPE_CHECKING
from snakemake_interface_storage_plugins.settings import (
    StorageProviderSettingsBase,
)
from snakemake_interface_storage_plugins import common

from snakemake_interface_common.plugin_registry.plugin import PluginBase

from snakemake_interface_storage_plugins.storage_object import (
    StorageObjectRead,
    StorageObjectWrite,
)


if TYPE_CHECKING:
    from snakemake_interface_storage_plugins.storage_provider import StorageProviderBase
    from snakemake_interface_storage_plugins.storage_object import StorageObjectBase


@dataclass
class Plugin(PluginBase[StorageProviderSettingsBase]):
    storage_provider: Type["StorageProviderBase"]
    storage_object: Type["StorageObjectBase"]
    _storage_settings_cls: Optional[Type[StorageProviderSettingsBase]]
    _name: str

    @property
    def support_tagged_values(self) -> bool:
        return True

    @property
    def name(self) -> str:
        return self._name

    @property
    def cli_prefix(self) -> str:
        return "storage-" + self.name.replace(common.storage_plugin_module_prefix, "")

    @property
    def settings_cls(self) -> Optional[Type[StorageProviderSettingsBase]]:
        return self._storage_settings_cls

    @property
    def is_read_write(self) -> bool:
        return issubclass(self.storage_object, StorageObjectWrite) and issubclass(
            self.storage_object, StorageObjectRead
        )
