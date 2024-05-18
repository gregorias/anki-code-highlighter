from codehighlighter.serialization import IdentityJSONObjectConverter, JSONObjectSerializer

import unittest


class SerializationTestCase(unittest.TestCase):

    def test_dict_serializer(self):
        foo = {"foo": "bar"}
        foo_serializer = JSONObjectSerializer(IdentityJSONObjectConverter())

        self.assertEqual(foo_serializer.dump(foo), "{\"foo\": \"bar\"}")
        self.assertEqual(foo_serializer.load("{\"foo\": \"bar\"}"), foo)

    def test_dict_load_handles_errors(self):
        foo_serializer = JSONObjectSerializer(IdentityJSONObjectConverter())
        self.assertIsNone(foo_serializer.load("foo"))
