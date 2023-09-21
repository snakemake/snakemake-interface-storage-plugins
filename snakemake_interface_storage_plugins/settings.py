from dataclasses import dataclass


import snakemake_interface_common.plugin_registry.plugin


@dataclass
class StorageSettingsBase(
    snakemake_interface_common.plugin_registry.plugin.SettingsBase
):
    """Base class for storage plugin settings.

    Storage plugins can define a subclass of this class,
    named 'StorageSettings'.
    """

    pass