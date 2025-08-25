import unittest

from codehighlighter.ankieditorextra import (
    SelectedText,
)
from codehighlighter.clipboard import EmptyClipboard, StubClipboard
from codehighlighter.dialog import DISPLAY_STYLE, PygmentsConfig
from codehighlighter.main import highlight, highlight_selection

from .test_ankieditorextra import MockEditorInterface


class HighlightTestCase(unittest.TestCase):

    def test_highlights_pygments_python_code(self):
        editor = MockEditorInterface(SelectedText("123"))
        err_msg = None

        def on_error(msg):
            nonlocal err_msg
            err_msg = msg

        highlight(
            highlighter_config_factory=lambda: PygmentsConfig(
                display_style=DISPLAY_STYLE.INLINE, language="python"
            ),
            block_style="",
            clipboard=EmptyClipboard(),
            editor=editor,
            on_error=on_error,
        )

        self.assertIsNone(err_msg)
        self.assertEqual(
            '\'<code class="pygments">' + '<span class="mi">123</span>' + "</code>'",
            editor.unwrap_action.contents,
        )


class HighlightSelectionTestCase(unittest.TestCase):

    def test_highlights_pygments_python_code(self):
        result = highlight_selection(
            code="return 123",
            highlighter_config_factory=lambda: PygmentsConfig(
                display_style=DISPLAY_STYLE.INLINE, language="python"
            ),
            block_style="display:flex; justify-content:center;",
            clipboard=EmptyClipboard(),
        )

        self.assertEqual(
            '<code class="pygments">'
            + '<span class="k">return</span> <span class="mi">123</span>'
            + "</code>",
            str(result),
        )

    def test_quits_on_no_config(self):
        result = highlight_selection(
            code="return 123",
            highlighter_config_factory=lambda: None,
            block_style="display:flex; justify-content:center;",
            clipboard=EmptyClipboard(),
        )

        self.assertIsNone(result)

    def test_uses_clipboard_on_empty_selection(self):
        result = highlight_selection(
            code="",
            highlighter_config_factory=lambda: PygmentsConfig(
                display_style=DISPLAY_STYLE.INLINE, language="python"
            ),
            block_style="",
            clipboard=StubClipboard("123"),
        )

        self.assertEqual(
            '<code class="pygments">' + '<span class="mi">123</span>' + "</code>",
            str(result),
        )
