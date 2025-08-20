__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from abc import abstractmethod
import re
from typing import Dict
from typing import Optional


WILDCARD_REGEX = re.compile(
    r"""
    \{
        (?=(   # This lookahead assertion emulates an 'atomic group'
               # which is required for performance
            \s*(?P<name>[.\w]+)   # wildcard name
            (\s*,\s*
                (?P<constraint>                 # an optional constraint
                    ([^{}]+ | \{\d+(,\d+)?\})*  # allow curly braces to nest one level
                )                               # ...  as in '{w,a{3,5}}'
            )?\s*
        ))\1
    \}
    """,
    re.VERBOSE,
)


def get_constant_prefix(pattern: str, strip_incomplete_parts: bool = False) -> str:
    """Return constant prefix of a pattern, removing everything from the first
    wildcard on.

    If strip_incomplete_parts is set, trailing parts that do not end with
    a slash (/) are removed as well.
    """
    first_wildcard = WILDCARD_REGEX.search(pattern)
    if first_wildcard:
        prefix = pattern[: first_wildcard.start()]
        if strip_incomplete_parts:
            if "/" in prefix:
                prefix = prefix.rsplit("/", 1)[0] + "/"
            else:
                first_slash_idx = pattern.find("/")
                if first_slash_idx != -1 and first_slash_idx > first_wildcard.start():
                    # the first slash is after the first wildcard, hence the prefix
                    # is incomplete
                    prefix = ""
    else:
        prefix = pattern

    return prefix


class Mtime:
    __slots__ = ["_local", "_local_target", "_storage"]
    _local: Optional[float]
    _local_target: Optional[float]
    _storage: Optional[float]

    def __init__(
        self,
        local: Optional[float] = None,
        local_target: Optional[float] = None,
        storage: Optional[float] = None,
    ):
        self._local = local
        self._local_target = local_target
        self._storage = storage

    def local_or_storage(self, follow_symlinks: bool = False) -> Optional[float]:
        if self._storage is not None:
            return self._storage
        return self.local(follow_symlinks=follow_symlinks)

    def storage(
        self,
    ) -> Optional[float]:
        return self._storage

    def local(self, follow_symlinks: bool = False) -> Optional[float]:
        if follow_symlinks and self._local_target is not None:
            return self._local_target
        return self._local


class IOCacheStorageInterface:
    @property
    @abstractmethod
    def exists_local(self) -> Dict[str, bool]: ...

    @property
    @abstractmethod
    def exists_in_storage(self) -> Dict[str, bool]: ...

    @property
    @abstractmethod
    def mtime(self) -> Dict[str, Mtime]: ...

    @property
    @abstractmethod
    def size(self) -> Dict[str, int]: ...
