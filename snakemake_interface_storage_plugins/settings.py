__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from dataclasses import dataclass, field
from typing import Optional


import snakemake_interface_common.plugin_registry.plugin


@dataclass
class StorageProviderSettingsBase(
    snakemake_interface_common.plugin_registry.plugin.SettingsBase
):
    """Base class for storage plugin settings.

    Storage plugins can define a subclass of this class,
    named 'StorageSettings'.
    """

    max_requests_per_second: Optional[float] = field(
        default=None,
        metadata={
            "help": "Maximum number of requests per second for this storage provider. "
            "If nothing is specified, the default implemented by the storage plugin is "
            "used."
        },
    )
