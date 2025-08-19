from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class QueryBase:
    """Base class for structured queries.
    
    By implementing the `to_str` method, subclasses can define how the query
    should be represented as a string or list of strings, representing individual
    queries.
    """
    # TODO determine how to auto-handle to and from str conversion
    # how to handle wildcards, and how to handle single queries representing multiple
    # individual queries. For the latter, can we use the same type or should we
    # use a different type?
    def to_str(self) -> List[str]: ...