import unittest
from unittest.mock import MagicMock, patch

from codehighlighter.ankieditorextra import (
    SelectedText,
)
from codehighlighter.clipboard import EmptyClipboard, StubClipboard
from codehighlighter.dialog import DISPLAY_STYLE, PygmentsConfig
from codehighlighter.main import (
    DEFAULT_CSS_ASSETS,
    highlight,
    highlight_selection,
    sync_assets_hook,
)

from .in_memory_config import InMemoryConfig
from .test_ankieditorextra import MockEditorInterface


class HighlightTestCase(unittest.TestCase):

    @patch(
        "codehighlighter.main.config",
        new=InMemoryConfig({"auto-detect-display-style": True}),
    )
    def test_highlights_pygments_python_code(self):
        editor = MockEditorInterface(SelectedText("123"))
        err_msg = None

        def on_error(msg):
            nonlocal err_msg
            err_msg = msg

        highlight(
            highlighter_config_factory=lambda preselected: PygmentsConfig(
                display_style=DISPLAY_STYLE.INLINE, language="python"
            ),
            block_style="",
            clipboard=EmptyClipboard(),
            editor=editor,
            on_error=on_error,
        )

        self.assertIsNone(err_msg)
        self.assertEqual(
            '\'<code class="gch-pygments"><!-- gch-lang: python -->'
            + '<span class="mi">123</span>'
            + "</code>'",
            editor.unwrap_action.contents,
        )


class HighlightSelectionTestCase(unittest.TestCase):

    def test_highlights_pygments_python_code(self):
        result = highlight_selection(
            code="return 123",
            highlighter_config_factory=lambda preselected: PygmentsConfig(
                display_style=DISPLAY_STYLE.INLINE, language="python"
            ),
            block_style="display:flex; justify-content:center;",
            clipboard=EmptyClipboard(),
        )

        self.assertEqual(
            '<code class="gch-pygments"><!-- gch-lang: python -->'
            + '<span class="k">return</span> <span class="mi">123</span>'
            + "</code>",
            str(result),
        )

    def test_quits_on_no_config(self):
        result = highlight_selection(
            code="return 123",
            highlighter_config_factory=lambda preselected: None,
            block_style="display:flex; justify-content:center;",
            clipboard=EmptyClipboard(),
        )

        self.assertIsNone(result)

    def test_uses_clipboard_on_empty_selection(self):
        result = highlight_selection(
            code="",
            highlighter_config_factory=lambda preselected: PygmentsConfig(
                display_style=DISPLAY_STYLE.INLINE, language="python"
            ),
            block_style="",
            clipboard=StubClipboard("123"),
        )

        self.assertEqual(
            '<code class="gch-pygments"><!-- gch-lang: python -->'
            + '<span class="mi">123</span>'
            + "</code>",
            str(result),
        )

    @patch(
        "codehighlighter.main.config",
        new=InMemoryConfig({"auto-detect-display-style": False}),
    )
    def test_auto_detect_display_style_disabled(self):
        recorded_preselected = None

        def factory(preselected):
            nonlocal recorded_preselected
            recorded_preselected = preselected
            return PygmentsConfig(display_style=DISPLAY_STYLE.INLINE, language="python")

        highlight_selection(
            code="line 1\nline 2",
            highlighter_config_factory=factory,
            block_style="",
            clipboard=EmptyClipboard(),
            auto_detect_display_style=False,
        )
        self.assertIsNone(recorded_preselected.display_style)

    @patch(
        "codehighlighter.main.config",
        new=InMemoryConfig({"auto-detect-display-style": True}),
    )
    def test_auto_detect_display_style_enabled_single_line(self):
        recorded_preselected = None

        def factory(preselected):
            nonlocal recorded_preselected
            recorded_preselected = preselected
            return PygmentsConfig(display_style=DISPLAY_STYLE.INLINE, language="python")

        highlight_selection(
            code="single line",
            highlighter_config_factory=factory,
            block_style="",
            clipboard=EmptyClipboard(),
            auto_detect_display_style=True,
        )
        self.assertIsNone(recorded_preselected.display_style)

    @patch(
        "codehighlighter.main.config",
        new=InMemoryConfig({"auto-detect-display-style": True}),
    )
    def test_auto_detect_display_style_enabled_multi_line(self):
        recorded_preselected = None

        def factory(preselected):
            nonlocal recorded_preselected
            recorded_preselected = preselected
            return PygmentsConfig(display_style=DISPLAY_STYLE.INLINE, language="python")

        highlight_selection(
            code="line 1\nline 2",
            highlighter_config_factory=factory,
            block_style="",
            clipboard=EmptyClipboard(),
            auto_detect_display_style=True,
        )
        self.assertEqual(recorded_preselected.display_style, DISPLAY_STYLE.BLOCK)


class SyncAssetsHookTestCase(unittest.TestCase):

    @patch("codehighlighter.main.mw", None)
    @patch("codehighlighter.main.showWarning")
    @patch("codehighlighter.main.create_anki_asset_manager")
    @patch("codehighlighter.main.config", new=InMemoryConfig())
    def test_mw_is_none_shows_warning_and_does_not_run(
        self, mock_create_manager, mock_show_warning
    ):
        fake_manager = MagicMock()
        mock_create_manager.return_value = fake_manager

        sync_assets_hook()

        mock_show_warning.assert_called_once()
        mock_create_manager.assert_not_called()
        fake_manager.install_assets.assert_not_called()

    @patch("codehighlighter.main.mw")
    @patch("codehighlighter.main.showWarning")
    @patch("codehighlighter.main.create_anki_asset_manager")
    @patch("codehighlighter.main.config", new=InMemoryConfig())
    def test_mw_col_is_none_shows_warning_and_does_not_run(
        self, mock_create_manager, mock_show_warning, mock_mw
    ):
        mock_mw.col = None
        fake_manager = MagicMock()
        mock_create_manager.return_value = fake_manager

        sync_assets_hook()

        mock_show_warning.assert_called_once()
        mock_create_manager.assert_not_called()
        fake_manager.install_assets.assert_not_called()

    @patch("codehighlighter.main.mw")
    @patch("codehighlighter.main.showWarning")
    @patch("codehighlighter.main.create_anki_asset_manager")
    @patch("codehighlighter.main.has_newer_version")
    @patch("codehighlighter.main.config", new=InMemoryConfig())
    def test_deps_are_present_has_newer_version_runs_sync(
        self, mock_has_newer_version, mock_create_manager, mock_show_warning, mock_mw
    ):
        mock_mw.col = MagicMock()
        mock_has_newer_version.return_value = True
        fake_manager = MagicMock()
        mock_create_manager.return_value = fake_manager

        sync_assets_hook()

        mock_show_warning.assert_not_called()
        mock_create_manager.assert_called_once_with(DEFAULT_CSS_ASSETS, mock_mw.col)
        fake_manager.delete_assets.assert_called_once()
        fake_manager.install_assets.assert_called_once()

    @patch("codehighlighter.main.mw")
    @patch("codehighlighter.main.showWarning")
    @patch("codehighlighter.main.create_anki_asset_manager")
    @patch("codehighlighter.main.has_newer_version")
    @patch(
        "codehighlighter.main.config",
        new=InMemoryConfig({"auto-update-media": False}),
    )
    def test_deps_are_present_has_newer_version_but_user_disabled_does_not_run(
        self, mock_has_newer_version, mock_create_manager, mock_show_warning, mock_mw
    ):
        mock_mw.col = MagicMock()
        mock_has_newer_version.return_value = True
        fake_manager = MagicMock()
        mock_create_manager.return_value = fake_manager

        sync_assets_hook()

        mock_show_warning.assert_not_called()
        mock_create_manager.assert_not_called()
        fake_manager.install_assets.assert_not_called()
