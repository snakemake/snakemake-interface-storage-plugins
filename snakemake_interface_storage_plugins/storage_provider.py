__author__ = "Christopher Tomkins-Tinch"
__copyright__ = "Copyright 2022, Christopher Tomkins-Tinch"
__email__ = "tomkinsc@broadinstitute.org"
__license__ = "MIT"


from dataclasses import dataclass
import os
import sys
from abc import ABC, ABCMeta, abstractmethod
from snakemake_interface_storage_plugins.io import MaybeAnnotated, flag, glob_wildcards, is_flagged

from snakemake_interface_storage_plugins.storage_object import StaticStorageObjectProxy


@dataclass
class StorageProviderBase(ABC):
    """This is an abstract class to be used to derive remote provider classes. These might be used to hold common credentials,
    and are then passed to StorageObjects.
    """

    supports_default = False

    def __init__(
        self, *args, keep_local=False, stay_on_remote=False, is_default=False, **kwargs
    ):
        self.args = args
        self.stay_on_remote = stay_on_remote
        self.keep_local = keep_local
        self.is_default = is_default
        self.kwargs = kwargs

    def object(
        self, value: MaybeAnnotated, *args, keep_local=None, stay_on_remote=None, static=False, **kwargs
    ):
        if is_flagged(value, "temp"):
            raise SyntaxError("Remote and temporary flags are mutually exclusive.")
        if is_flagged(value, "protected"):
            raise SyntaxError("Remote and protected flags are mutually exclusive.")
        if keep_local is None:
            keep_local = self.keep_local
        if stay_on_remote is None:
            stay_on_remote = self.stay_on_remote

        def _set_protocol(value):
            """Adds the default protocol to `value` if it doesn't already have one"""
            protocol = self.default_protocol
            for p in self.available_protocols:
                if value.startswith(p):
                    value = value[len(p) :]
                    protocol = p
                    break
            return protocol, value

        if isinstance(value, str):
            protocol, value = _set_protocol(value)
            value = protocol + value if stay_on_remote else value
        else:
            protocol, value = list(zip(*[_set_protocol(v) for v in value]))
            if len(set(protocol)) != 1:
                raise SyntaxError("A single protocol must be used per RemoteObject")
            protocol = set(protocol).pop()
            value = [protocol + v if stay_on_remote else v for v in value]

        if "protocol" not in kwargs:
            if "protocol" not in self.kwargs:
                kwargs["protocol"] = protocol
            else:
                kwargs["protocol"] = self.kwargs["protocol"]

        provider = sys.modules[self.__module__]  # get module of derived class
        remote_object = provider.RemoteObject(
            *args,
            keep_local=keep_local,
            stay_on_remote=stay_on_remote,
            provider=self,
            **kwargs,
        )
        if static:
            remote_object = StaticStorageObjectProxy(remote_object)
        return flag(value, "remote_object", remote_object)

    def glob_wildcards(self, pattern, *args, **kwargs):
        args = self.args if not args else args
        kwargs = self.kwargs if not kwargs else kwargs

        reference_obj = self.object(pattern, *args, **kwargs)
        remote_object = reference_obj.flags["remote_object"]
        if not remote_object.stay_on_remote:
            pattern = "./" + remote_object.name
            pattern = os.path.normpath(pattern)

        key_list = [k for k in remote_object.list]

        return glob_wildcards(pattern, files=key_list)

    @abstractmethod
    def default_protocol(self):
        """The protocol that is prepended to the path when no protocol is specified."""
        pass

    @abstractmethod
    def available_protocols(self):
        """List of valid protocols for this remote provider."""
        pass

    @property
    def name(self):
        return self.__module__.split(".")[-1]
