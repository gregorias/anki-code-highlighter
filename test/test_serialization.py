import unittest
from typing import Optional, TypeVar

from codehighlighter.serialization import (
    JSONObjectConverter,
    JSONObjectSerializer,
)

T = TypeVar("T")


class IdentityJSONObjectConverter(JSONObjectConverter[T]):
    """A converter that does nothing."""

    def deconvert(self, json_object) -> Optional[T]:
        return json_object

    def convert(self, t: T):
        return t


class SerializationTestCase(unittest.TestCase):

    def test_dict_serializer(self):
        foo = {"foo": "bar"}
        foo_serializer = JSONObjectSerializer(IdentityJSONObjectConverter())

        self.assertEqual(foo_serializer.dump(foo), "{\"foo\": \"bar\"}")
        self.assertEqual(foo_serializer.load("{\"foo\": \"bar\"}"), foo)

    def test_dict_load_handles_errors(self):
        foo_serializer = JSONObjectSerializer(IdentityJSONObjectConverter())
        self.assertIsNone(foo_serializer.load("foo"))
