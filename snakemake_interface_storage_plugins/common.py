__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"


from enum import Enum
from pathlib import Path
import shutil


storage_plugin_prefix = "snakemake-storage-plugin-"
storage_plugin_module_prefix = storage_plugin_prefix.replace("-", "_")


class Operation(Enum):
    RETRIEVE = "retrieve"
    STORE = "store"
    EXISTS = "exists"
    MTIME = "mtime"
    REMOVE = "remove"
    SIZE = "size"
    TOUCH = "touch"


def get_disk_free(local_path: Path) -> int:
    # go up in hierarchy until the local path is present
    # this ensures that the disk usage is calculated for the correct partition
    while not local_path.exists():
        local_path = local_path.parent
    return shutil.disk_usage(local_path).free
