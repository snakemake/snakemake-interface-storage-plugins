from pathlib import Path
from typing import Optional

from snakemake_interface_common.exceptions import WorkflowError


class FileOrDirectoryNotFoundError(WorkflowError):
    def __init__(self, local_path: Path, query: Optional[str] = None):
        self.query: Optional[str] = query
        self.local_path: Path = local_path
        msg = (
            f"Storage object {query} not found in storage (local path: {local_path!s})."
            if query
            else f"File or directory not found: {local_path!s}"
        )
        super().__init__(msg)

    def is_for_path(self, path: Path) -> bool:
        return self.local_path.resolve() == path.resolve()
