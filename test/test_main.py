import unittest
from unittest.mock import MagicMock, patch

from codehighlighter import hljs
from codehighlighter.ankieditorextra import (
    SelectedText,
)
from codehighlighter.clipboard import EmptyClipboard, StubClipboard
from codehighlighter.dialog import DISPLAY_STYLE, HljsConfig, PygmentsConfig
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

    def test_highlights_hljs_python_block(self):
        result = highlight_selection(
            code="return 123",
            highlighter_config_factory=lambda: HljsConfig(
                language=hljs.get_available_languages_as_dict()["Python"]
            ),
            block_style="display:flex; justify-content:center;",
            clipboard=EmptyClipboard(),
        )

        self.assertEqual(
            '<pre style="display:flex; justify-content:center;">'
            + '<code class="language-python">return 123</code>'
            + "</pre>",
            str(result),
        )

    def test_highlights_hljs_plaintext_code(self):
        result = highlight_selection(
            code="return 123",
            highlighter_config_factory=lambda: HljsConfig(language=None),
            block_style="",
            clipboard=EmptyClipboard(),
        )

        self.assertEqual(
            "<pre>" + '<code class="nohighlight">return 123</code>' + "</pre>",
            str(result),
        )

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


class ShowDeprecationWarningTestCase(unittest.TestCase):

    @patch("codehighlighter.main.QMessageBox")
    @patch("codehighlighter.main.Path")
    def test_does_not_show_if_sentinel_exists(self, mock_path_class, mock_qmessagebox):
        mock_mw = MagicMock()
        mock_mw.col.media.dir.return_value = "/mock/media/dir"

        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_sentinel_path = MagicMock()
        mock_path_instance.__truediv__.return_value = mock_sentinel_path
        mock_sentinel_path.exists.return_value = True

        from codehighlighter.main import show_deprecation_warning_if_needed

        show_deprecation_warning_if_needed(mock_mw)

        mock_sentinel_path.exists.assert_called_once()
        mock_qmessagebox.assert_not_called()

    @patch("codehighlighter.main.QMessageBox")
    @patch("codehighlighter.main.Path")
    def test_shows_if_sentinel_does_not_exist_and_remind_later(
        self, mock_path_class, mock_qmessagebox
    ):
        mock_mw = MagicMock()
        mock_mw.col.media.dir.return_value = "/mock/media/dir"

        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_sentinel_path = MagicMock()
        mock_path_instance.__truediv__.return_value = mock_sentinel_path
        mock_sentinel_path.exists.return_value = False

        mock_mb = mock_qmessagebox.return_value
        mock_mb.clickedButton.return_value = (
            MagicMock()
        )  # something other than dont_show_btn

        from codehighlighter.main import show_deprecation_warning_if_needed

        show_deprecation_warning_if_needed(mock_mw)

        mock_sentinel_path.exists.assert_called_once()
        mock_qmessagebox.assert_called_once_with(mock_mw)
        mock_mb.exec.assert_called_once()
        mock_sentinel_path.write_text.assert_not_called()

    @patch("codehighlighter.main.QMessageBox")
    @patch("codehighlighter.main.Path")
    def test_shows_if_sentinel_does_not_exist_and_dont_show_again(
        self, mock_path_class, mock_qmessagebox
    ):
        mock_mw = MagicMock()
        mock_mw.col.media.dir.return_value = "/mock/media/dir"

        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_sentinel_path = MagicMock()
        mock_path_instance.__truediv__.return_value = mock_sentinel_path
        mock_sentinel_path.exists.return_value = False

        mock_mb = mock_qmessagebox.return_value
        mock_dont_show_btn = MagicMock()
        mock_mb.addButton.side_effect = lambda text, role: (
            mock_dont_show_btn if "Don" in text else MagicMock()
        )
        mock_mb.clickedButton.return_value = mock_dont_show_btn

        from codehighlighter.main import show_deprecation_warning_if_needed

        show_deprecation_warning_if_needed(mock_mw)

        mock_sentinel_path.exists.assert_called_once()
        mock_qmessagebox.assert_called_once_with(mock_mw)
        mock_mb.exec.assert_called_once()
        mock_sentinel_path.write_text.assert_called_once_with(
            "dismissed", encoding="utf-8"
        )
