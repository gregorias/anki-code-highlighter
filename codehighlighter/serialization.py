"""Utilities related to serialization."""

import json
import typing
from typing import Optional, Protocol

T = typing.TypeVar("T")


class JSONObjectConverter(Protocol[T]):
    """A converter to and from JSON serializable objects."""

    def deconvert(self, json_object) -> Optional[T]:
        return None

    def convert(self, t: T) -> str:
        ...


class Serializer(Protocol[T]):
    """A JSON serialization protocol."""

    def load(self, content: str) -> Optional[T]:
        return None

    def dump(self, t: T) -> str:
        pass


class JSONObjectSerializer(Serializer[T]):
    """A JSON serialization protocol that uses a JSON object converter."""

    def __init__(self, converter: JSONObjectConverter[T]):
        self.converter = converter

    def load(self, content: str) -> Optional[T]:
        try:
            return self.converter.deconvert(json.loads(content))
        except json.JSONDecodeError:
            return None

    def dump(self, t: T) -> str:
        return json.dumps(self.converter.convert(t))
