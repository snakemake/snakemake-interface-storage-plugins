__author__ = "Christopher Tomkins-Tinch, Johannes Köster"
__copyright__ = "Copyright 2023, Christopher Tomkins-Tinch, Johannes Köster"
__email__ = "tomkinsc@broadinstitute.org"
__license__ = "MIT"

import os
import sys
import re
from functools import partial
from abc import ABC, ABCMeta, abstractmethod
from contextlib import contextmanager
import shutil

from wrapt import ObjectProxy
from reretry import retry
from connection_pool import ConnectionPool
import copy

from snakemake_interface_common.exceptions import WorkflowError
from snakemake_interface_common.logging import get_logger

from snakemake_interface_storage_plugins.io import IOCacheStorageInterface


class StaticStorageObjectProxy(ObjectProxy):
    """Proxy that implements static-ness for remote objects.

    The constructor takes a real RemoteObject and returns a proxy that
    behaves the same except for the exists() and mtime() methods.

    """

    def exists(self):
        return True

    def mtime(self):
        return float("-inf")

    def is_newer(self, time):
        return False

    def __copy__(self):
        copied_wrapped = copy.copy(self.__wrapped__)
        return type(self)(copied_wrapped)

    def __deepcopy__(self, memo):
        copied_wrapped = copy.deepcopy(self.__wrapped__, memo)
        return type(self)(copied_wrapped)


class AbstractStorageObject(ABC):
    """This is an abstract class to be used to derive remote object classes for
    different cloud storage providers. For example, there could be classes for interacting with
    Amazon AWS S3 and Google Cloud Storage, both derived from this common base class.
    """

    def __init__(
        self,
        *args,
        protocol=None,
        keep_local=False,
        stay_on_remote=False,
        provider=None,
        **kwargs,
    ):
        assert protocol is not None
        # self._iofile must be set before the remote object can be used, in io.py or elsewhere
        self._iofile = None
        self.args = args
        self.kwargs = kwargs

        self.keep_local = keep_local
        self.stay_on_remote = stay_on_remote
        self.provider = provider
        self.protocol = protocol

    async def inventory(self, cache: IOCacheStorageInterface):
        """From this file, try to find as much existence and modification date
        information as possible.
        """
        # If this is implemented in a remote object, results have to be stored in
        # the given IOCache object.
        pass

    @abstractmethod
    def get_inventory_parent(self):
        pass

    @property
    def _file(self):
        if self._iofile is None:
            return None
        return self._iofile._file

    def file(self):
        return self._file

    def local_file(self):
        if self.stay_on_remote:
            return self._file[len(self.protocol) :]
        else:
            return self._file

    def remote_file(self):
        return self.protocol + self.local_file()

    def to_plainstr(self):
        if self.stay_on_remote:
            return str(self.remote_file())
        else:
            return str(self.local_file())

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def exists(self):
        pass

    @abstractmethod
    def mtime(self):
        pass

    @abstractmethod
    def size(self):
        pass

    def download(self):
        try:
            return self._download()
        except Exception as e:
            local_path = self.local_file()
            if os.path.exists(local_path):
                if os.path.isdir(local_path):
                    shutil.rmtree(local_path)
                os.remove(local_path)
            raise WorkflowError(e)

    def upload(self):
        try:
            self._upload()
        except Exception as e:
            raise WorkflowError(e)

    @abstractmethod
    def _download(self, *args, **kwargs):
        pass

    @abstractmethod
    def _upload(self, *args, **kwargs):
        pass

    @abstractmethod
    def list(self, *args, **kwargs):
        pass

    @abstractmethod
    def name(self, *args, **kwargs):
        pass

    @abstractmethod
    def remove(self):
        raise NotImplementedError("Removal of files is unavailable for this remote")

    def local_touch_or_create(self):
        self._iofile.touch_or_create()


class AbstractStorageRetryObject(AbstractStorageObject, ABC):
    @retry(tries=3, delay=3, backoff=2, logger=get_logger())
    def download(self):
        return super().download()

    @retry(tries=3, delay=3, backoff=2, logger=get_logger())
    def upload(self):
        super().upload()


class DomainObject(AbstractStorageRetryObject, ABC):
    """This is a mixin related to parsing components
    out of a location path specified as
    (host|IP):port/remote/location
    """

    def __init__(self, *args, **kwargs):
        super(DomainObject, self).__init__(*args, **kwargs)

    @property
    def _matched_address(self):
        return re.search(
            r"^(?P<protocol>[a-zA-Z]+\://)?(?P<host>[A-Za-z0-9\-\.]+)(?:\:(?P<port>[0-9]+))?(?P<path_remainder>.*)$",
            self.local_file(),
        )

    @property
    def name(self):
        return self.path_remainder

    # if we ever parse out the protocol directly
    # @property
    # def protocol(self):
    #    if self._matched_address:
    #        return self._matched_address.group("protocol")

    @property
    def host(self):
        if self._matched_address:
            return self._matched_address.group("host")

    @property
    def port(self):
        if self._matched_address:
            return self._matched_address.group("port")

    @property
    def path_prefix(self):
        # this is the domain and port, however specified before the path remainder
        return self._iofile._file[: self._iofile._file.index(self.path_remainder)]

    @property
    def path_remainder(self):
        if self._matched_address:
            return self._matched_address.group("path_remainder")

    @property
    def local_path(self):
        return self._iofile._file

    @property
    def remote_path(self):
        return self.path_remainder


class PooledDomainObject(DomainObject, ABC):
    """This adds connection pooling to DomainObjects
    out of a location path specified as
    (host|IP):port/remote/location
    """

    connection_pools = {}

    def __init__(self, *args, pool_size=100, immediate_close=False, **kwargs):
        super(PooledDomainObject, self).__init__(*args, **kwargs)
        self.pool_size = 100
        self.immediate_close = immediate_close

    def get_default_kwargs(self, **defaults):
        defaults.setdefault("host", self.host)
        defaults.setdefault("port", int(self.port) if self.port else None)
        return defaults

    def get_args_to_use(self):
        """merge the objects args with the parent provider

        Positional Args: use those of object or fall back to ones from provider
        Keyword Args: merge with any defaults
        """
        # if args have been provided to remote(),
        #  use them over those given to RemoteProvider()
        args_to_use = self.provider.args
        if len(self.args):
            args_to_use = self.args

        # use kwargs passed in to remote() to override those given to the RemoteProvider()
        #  default to the host and port given as part of the file,
        #  falling back to one specified as a kwarg to remote() or the RemoteProvider
        #  (overriding the latter with the former if both)
        kwargs_to_use = self.get_default_kwargs()
        for k, v in self.provider.kwargs.items():
            kwargs_to_use[k] = v
        for k, v in self.kwargs.items():
            kwargs_to_use[k] = v

        return args_to_use, kwargs_to_use

    @contextmanager
    def get_connection(self):
        """get a connection from a pool or create a new one"""
        if not self.immediate_close and "connection_pool" in sys.modules:
            # if we can (and the user doesn't override) use a pool
            with self.connection_pool.item() as conn:
                yield conn
        else:
            # otherwise create a one-time connection
            args_to_use, kwargs_to_use = self.get_args_to_use()
            conn = self.create_connection(*args_to_use, **kwargs_to_use)
            try:
                yield conn
            finally:
                self.close_connection(conn)

    @property
    def conn_keywords(self):
        """returns list of keywords relevant to a unique connection"""
        return ["host", "port", "username"]

    @property
    def connection_pool(self):
        """set up a pool of re-usable active connections"""
        # merge this object's values with those of its parent provider
        args_to_use, kwargs_to_use = self.get_args_to_use()

        # hashing connection pool on tuple of relevant arguments. There
        # may be a better way to do this
        conn_pool_label_tuple = (
            type(self),
            *args_to_use,
            *[kwargs_to_use.get(k, None) for k in self.conn_keywords],
        )

        if conn_pool_label_tuple not in self.connection_pools:
            create_callback = partial(
                self.create_connection, *args_to_use, **kwargs_to_use
            )
            self.connection_pools[conn_pool_label_tuple] = ConnectionPool(
                create_callback, close=self.close_connection, max_size=self.pool_size
            )

        return self.connection_pools[conn_pool_label_tuple]

    @abstractmethod
    def create_connection(self):
        """handle the protocol specific job of creating a connection"""
        pass

    @abstractmethod
    def close_connection(self, connection):
        """handle the protocol specific job of closing a connection"""
        pass
