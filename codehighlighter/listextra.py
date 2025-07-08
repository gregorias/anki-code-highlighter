"""Extra utilities for lists."""

from typing import List, Optional, TypeVar

__all__ = ["index_or"]

T = TypeVar("T")


def index_or(ls: List[T], item: T, default: Optional[int]) -> Optional[int]:
    """
    Like list.index, but does not throw and returns a default value instead.
    """
    try:
        return ls.index(item)
    except ValueError:
        return default
