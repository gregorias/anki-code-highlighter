"""Utilities related to serialization."""

import json
from typing import Optional, Protocol
import typing

T = typing.TypeVar("T")


class JSONObjectConverter(Protocol[T]):
    """A converter to and from JSON serializable objects."""

    def deconvert(self, json_object) -> Optional[T]:
        return None

    def convert(self, t: T):
        pass


class IdentityJSONObjectConverter(JSONObjectConverter[T]):
    """A converter that does nothing."""

    def deconvert(self, json_object) -> Optional[T]:
        return json_object

    def convert(self, t: T):
        return t


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
