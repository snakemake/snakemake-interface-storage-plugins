__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "johannes.koester@uni-due.de"
__license__ = "MIT"

from abc import ABC, abstractmethod
import collections
from itertools import chain
import os
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


class AnnotatedStringStorageInterface(ABC):
    @property
    @abstractmethod
    def flags(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    def is_callable(self) -> bool:
        ...

    def is_flagged(self, flag: str) -> bool:
        return flag in self.flags and self.flags[flag]


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


def regex_from_filepattern(filepattern):
    f = []
    last = 0
    wildcards = set()
    for match in WILDCARD_REGEX.finditer(filepattern):
        f.append(re.escape(filepattern[last : match.start()]))
        wildcard = match.group("name")
        if wildcard in wildcards:
            if match.group("constraint"):
                raise ValueError(
                    "Constraint regex must be defined only in the first "
                    "occurence of the wildcard in a string."
                )
            f.append(f"(?P={wildcard})")
        else:
            wildcards.add(wildcard)
            f.append(
                "(?P<{}>{})".format(
                    wildcard,
                    match.group("constraint") if match.group("constraint") else ".+",
                )
            )
        last = match.end()
    f.append(re.escape(filepattern[last:]))
    f.append("$")  # ensure that the match spans the whole file
    return "".join(f)


def glob_wildcards(pattern, files=None, followlinks=False):
    """
    Glob the values of the wildcards by matching the given pattern to the filesystem.
    Returns a named tuple with a list of values for each wildcard.
    """
    if is_flagged(pattern, "remote_object") and files is None:
        # for storage object patterns, we obtain the list of files from
        # the storage provider
        pattern = pattern.path_without_protocol()
        files = pattern.flags["remote_object"].list_all_below_ancestor()

    pattern = os.path.normpath(pattern)
    first_wildcard = re.search("{[^{]", pattern)
    dirname = (
        os.path.dirname(pattern[: first_wildcard.start()])
        if first_wildcard
        else os.path.dirname(pattern)
    )
    if not dirname:
        dirname = "."

    names = [match.group("name") for match in WILDCARD_REGEX.finditer(pattern)]
    Wildcards = collections.namedtuple("Wildcards", names)
    wildcards = Wildcards(*[list() for name in names])

    pattern = re.compile(regex_from_filepattern(pattern))

    if files is None:
        files = (
            os.path.normpath(os.path.join(dirpath, f))
            for dirpath, dirnames, filenames in os.walk(
                dirname, followlinks=followlinks
            )
            for f in chain(filenames, dirnames)
        )

    for f in files:
        match = re.match(pattern, f)
        if match:
            for name, value in match.groupdict().items():
                getattr(wildcards, name).append(value)
    return wildcards


class Mtime:
    __slots__ = ["_local", "_local_target", "_remote"]

    def __init__(self, local=None, local_target=None, remote=None):
        self._local = local
        self._local_target = local_target
        self._remote = remote

    def local_or_remote(self, follow_symlinks=False):
        if self._remote is not None:
            return self._remote
        if follow_symlinks and self._local_target is not None:
            return self._local_target
        return self._local

    def remote(
        self,
    ):
        return self._remote

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
