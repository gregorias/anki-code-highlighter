from codehighlighter.dialog import (HIGHLIGHT_METHOD,
                                    HighlightMethodJSONConverter,
                                    DISPLAY_STYLE, DisplayStyleJSONConverter)

import unittest


class HighlightMethodTestCase(unittest.TestCase):

    def test_json_object_conversion(self):
        converter = HighlightMethodJSONConverter()

        self.assertEqual(converter.convert(HIGHLIGHT_METHOD.HLJS),
                         "highlight.js")
        self.assertEqual(converter.deconvert("highlight.js"),
                         HIGHLIGHT_METHOD.HLJS)


class DisplayStyleJSONConverterTestCase(unittest.TestCase):

    def test_json_object_conversion(self):
        converter = DisplayStyleJSONConverter()

        self.assertEqual(
            converter.deconvert(converter.convert(DISPLAY_STYLE.BLOCK)),
            DISPLAY_STYLE.BLOCK)
        self.assertEqual(
            converter.deconvert(converter.convert(DISPLAY_STYLE.INLINE)),
            DISPLAY_STYLE.INLINE)
        self.assertIsNone(converter.deconvert("foo"))
