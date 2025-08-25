import json
import unittest

from codehighlighter.dialog import (
    DISPLAY_STYLE,
    HIGHLIGHT_METHOD,
    DisplayStyleJSONConverter,
    HighlighterWizardState,
    HighlighterWizardStateJSONConverter,
    HighlightMethodJSONConverter,
    PygmentsConfig,
    PygmentsConfigJSONConverter,
)


class HighlightMethodTestCase(unittest.TestCase):

    def test_json_object_conversion(self):
        converter = HighlightMethodJSONConverter()

        self.assertEqual(converter.convert(HIGHLIGHT_METHOD.PYGMENTS), "pygments")
        self.assertEqual(converter.deconvert("pygments"), HIGHLIGHT_METHOD.PYGMENTS)


class DisplayStyleJSONConverterTestCase(unittest.TestCase):

    def test_json_object_conversion(self):
        converter = DisplayStyleJSONConverter()

        self.assertEqual(
            converter.deconvert(converter.convert(DISPLAY_STYLE.BLOCK)),
            DISPLAY_STYLE.BLOCK,
        )
        self.assertEqual(
            converter.deconvert(converter.convert(DISPLAY_STYLE.INLINE)),
            DISPLAY_STYLE.INLINE,
        )
        self.assertIsNone(converter.deconvert("foo"))


class PygmentsConfigJSONConverterTestCase(unittest.TestCase):

    def setUp(self):
        self.converter = PygmentsConfigJSONConverter()

    def test_keeps_config(self):
        config = PygmentsConfig(DISPLAY_STYLE.BLOCK, "C++")
        self.assertEqual(
            self.converter.deconvert(self.converter.convert(config)), config
        )

    def test_conversion_is_serializable(self):
        config = PygmentsConfig(DISPLAY_STYLE.BLOCK, "C++")
        conversion = self.converter.convert(config)
        json.dumps(conversion)


class HighlighterWizardStateJSONConverterTestCase(unittest.TestCase):

    def setUp(self):
        self.converter = HighlighterWizardStateJSONConverter()

    def test_keeps_config(self):
        config = HighlighterWizardState(
            HIGHLIGHT_METHOD.PYGMENTS, PygmentsConfig(DISPLAY_STYLE.BLOCK, "C++")
        )
        self.assertEqual(
            self.converter.deconvert(self.converter.convert(config)), config
        )

    def test_conversion_is_serializable(self):
        config = HighlighterWizardState(
            HIGHLIGHT_METHOD.PYGMENTS, PygmentsConfig(DISPLAY_STYLE.BLOCK, "C++")
        )
        conversion = self.converter.convert(config)
        json.dumps(conversion)
