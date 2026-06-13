import json
import unittest
from unittest.mock import patch

from codehighlighter.dialog import (
    DISPLAY_STYLE,
    DisplayStyleJSONConverter,
    HighlighterWizardState,
    HighlighterWizardStateJSONConverter,
    PartialPygmentsConfig,
    PygmentsConfig,
    PygmentsConfigJSONConverter,
    ask_for_highlighter_config,
)


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
        config = HighlighterWizardState(PygmentsConfig(DISPLAY_STYLE.BLOCK, "C++"))
        self.assertEqual(
            self.converter.deconvert(self.converter.convert(config)), config
        )

    def test_conversion_is_serializable(self):
        config = HighlighterWizardState(PygmentsConfig(DISPLAY_STYLE.BLOCK, "C++"))
        conversion = self.converter.convert(config)
        json.dumps(conversion)


class AskForHighlighterConfigTestCase(unittest.TestCase):

    @patch("codehighlighter.dialog.ask_for_language")
    @patch("codehighlighter.dialog.ask_for_display_style")
    def test_preselected_display_style_skips_display_style_wizard(
        self, mock_ask_display_style, mock_ask_language
    ):
        mock_ask_language.return_value = "Python"
        state = HighlighterWizardState(PygmentsConfig(DISPLAY_STYLE.BLOCK, "C++"))
        preselected = PartialPygmentsConfig(
            display_style=DISPLAY_STYLE.INLINE, language=None
        )

        config, new_state = ask_for_highlighter_config(
            parent=None, preselected=preselected, state=state
        )

        mock_ask_display_style.assert_not_called()
        mock_ask_language.assert_called_once()
        self.assertIsNotNone(config)
        self.assertEqual(config.display_style, DISPLAY_STYLE.INLINE)
        self.assertEqual(config.language, "Python")
