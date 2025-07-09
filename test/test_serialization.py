import unittest
from typing import Any

from codehighlighter.serialization import (
    JSONObjectConverter,
    JSONObjectSerializer,
)


class IdentityJSONObjectConverter[T](JSONObjectConverter[T]):
    """A converter that does nothing."""

    def deconvert(self, json_object) -> T | None:
        return json_object

    def convert(self, t: T) -> Any:
        return t


class SerializationTestCase(unittest.TestCase):

    def test_dict_serializer(self):
        foo = {"foo": "bar"}
        foo_serializer = JSONObjectSerializer(IdentityJSONObjectConverter())

        self.assertEqual(foo_serializer.dumps(foo), '{"foo": "bar"}')
        self.assertEqual(foo_serializer.loads('{"foo": "bar"}'), foo)

    def test_dict_load_handles_errors(self):
        foo_serializer = JSONObjectSerializer(IdentityJSONObjectConverter())
        self.assertIsNone(foo_serializer.loads("foo"))
