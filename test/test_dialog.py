from codehighlighter.dialog import HIGHLIGHT_METHOD, HighlightMethodJSONConverter

import unittest


class HighlightMethodTestCase(unittest.TestCase):

    def test_json_object_conversion(self):
        converter = HighlightMethodJSONConverter()

        self.assertEqual(converter.convert(HIGHLIGHT_METHOD.HLJS),
                         "highlight.js")
        self.assertEqual(converter.deconvert("highlight.js"),
                         HIGHLIGHT_METHOD.HLJS)
