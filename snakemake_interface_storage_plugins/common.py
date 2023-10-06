__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"


from enum import Enum


storage_plugin_prefix = "snakemake-storage-plugin-"
storage_plugin_module_prefix = storage_plugin_prefix.replace("-", "_")


class Operation(Enum):
    RETRIEVE = "retrieve"
    STORE = "store"
    EXISTS = "exists"
    MTIME = "mtime"
    REMOVE = "remove"
    SIZE = "size"
