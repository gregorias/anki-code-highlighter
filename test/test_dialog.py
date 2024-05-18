from codehighlighter.dialog import (HIGHLIGHT_METHOD,
                                    HighlightMethodJSONConverter,
                                    DISPLAY_STYLE, DisplayStyleJSONConverter,
                                    HljsConfig, HljsConfigJSONConverter)
import codehighlighter.hljslangs as hljslangs

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


class HljsConfigJSONConverterTestCase(unittest.TestCase):

    def setUp(self):
        self.converter = HljsConfigJSONConverter()

    def test_keeps_null_object(self):
        null_hljs_config = HljsConfig(None)
        self.assertEqual(
            self.converter.deconvert(self.converter.convert(null_hljs_config)),
            null_hljs_config)

    def test_keeps_language(self):
        hljs_config = HljsConfig(hljslangs.languages[10])
        self.assertEqual(
            self.converter.deconvert(self.converter.convert(hljs_config)),
            hljs_config)
