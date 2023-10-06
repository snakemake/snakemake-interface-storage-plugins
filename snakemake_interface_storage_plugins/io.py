__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from abc import ABC, abstractmethod
import re
from typing import Any, Dict, Union

from snakemake_interface_common.utils import not_iterable


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


class AnnotatedStringStorageInterface(ABC):
    @property
    @abstractmethod
    def flags(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    def is_callable(self) -> bool:
        ...

    def is_flagged(self, flag: str) -> bool:
        return flag in self.flags and bool(self.flags[flag])


class AnnotatedString(str, AnnotatedStringStorageInterface):
    def __init__(self, value):
        self._flags = dict()
        self.callable = value if is_callable(value) else None

    def new_from(self, new_value):
        new = str.__new__(self.__class__, new_value)
        new.flags = self.flags
        new.callable = self.callable
        return new

    def is_callable(self) -> bool:
        return self.callable is not None

    @property
    def flags(self) -> Dict[str, Any]:
        return self._flags

    @flags.setter
    def flags(self, value):
        self._flags = value


MaybeAnnotated = Union[AnnotatedStringStorageInterface, str]


def is_flagged(value: MaybeAnnotated, flag: str) -> bool:
    if not isinstance(value, AnnotatedStringStorageInterface):
        return False
    return value.is_flagged(flag)


def flag(value, flag_type, flag_value=True):
    if isinstance(value, AnnotatedString):
        value.flags[flag_type] = flag_value
        return value
    if not_iterable(value):
        value = AnnotatedString(value)
        value.flags[flag_type] = flag_value
        return value
    return [flag(v, flag_type, flag_value=flag_value) for v in value]


def is_callable(value: Any):
    return callable(value) or (
        isinstance(value, AnnotatedStringStorageInterface) and value.is_callable()
    )


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
