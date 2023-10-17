__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from abc import abstractmethod
import re
from typing import Dict


WILDCARD_REGEX = re.compile(
    r"""
    \{
        (?=(   # This lookahead assertion emulates an 'atomic group'
               # which is required for performance
            \s*(?P<name>\w+)                    # wildcard name
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


def get_constant_prefix(pattern: str):
    first_wildcard = WILDCARD_REGEX.search(pattern)
    if first_wildcard:
        return pattern[: first_wildcard.start()]
    else:
        return pattern


class Mtime:
    __slots__ = ["_local", "_local_target", "_storage"]

    def __init__(self, local=None, local_target=None, storage=None):
        self._local = local
        self._local_target = local_target
        self._storage = storage

    def local_or_storage(self, follow_symlinks=False):
        if self._storage is not None:
            return self._storage
        if follow_symlinks and self._local_target is not None:
            return self._local_target
        return self._local

    def storage(
        self,
    ):
        return self._storage

    def local(self, follow_symlinks=False):
        if follow_symlinks and self._local_target is not None:
            return self._local_target
        return self._local


class IOCacheStorageInterface:
    @property
    @abstractmethod
    def exists_local(self) -> Dict[str, bool]:
        ...

    @property
    @abstractmethod
    def exists_remote(self) -> Dict[str, bool]:
        ...

    @property
    @abstractmethod
    def mtime(self) -> Dict[str, Mtime]:
        ...

    @property
    @abstractmethod
    def size(self) -> Dict[str, int]:
        ...
