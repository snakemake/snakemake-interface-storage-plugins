from pathlib import Path


class ObjectNotFoundError(Exception):
    def __init__(self, query: str, local_path: Path):
        self.query: str = query
        self.local_path: Path = local_path
        super().__init__(
            f"Storage object {query} not found in storage (local path: {local_path})."
        )
