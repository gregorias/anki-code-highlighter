"""Utilities related to serialization."""

import json
import typing
from typing import Protocol


class JSONObjectConverter[T](Protocol):
    """A converter to and from JSON serializable objects."""

    def deconvert(self, json_object: typing.Any) -> T | None: ...

    def convert(self, t: T) -> typing.Any: ...


class Serializer[T](Protocol):
    """A converter of Ts to strings."""

    def loads(self, content: str) -> T | None: ...

    def dumps(self, t: T) -> str: ...


class JSONObjectSerializer[T](Serializer):
    """A JSON serialization protocol that uses a JSON object converter."""

    def __init__(self, converter: JSONObjectConverter[T]):
        self.converter = converter

    def loads(self, content: str) -> T | None:
        try:
            return self.converter.deconvert(json.loads(content))
        except json.JSONDecodeError:
            return None

    def dumps(self, t: T) -> str:
        return json.dumps(self.converter.convert(t))
