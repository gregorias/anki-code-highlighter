"""The implementation of the code highlighter add-on."""

import os.path
import random
import sys
from functools import partial
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple

import aqt
import aqt.editor
import aqt.qt
import bs4
from aqt import gui_hooks, mw
from aqt.qt import QApplication
from aqt.utils import showWarning

sys.path.append(os.path.dirname(__file__))

import anki  # type: ignore
import anki.collection
import anki.media
import anki.notes

from . import config, pygments_highlighter
from .ankieditorextra import (
    AnkiEditorInterface,
    EditorInterface,
    SelectionException,
    transform_selection,
)
from .assets import (
    AnkiAssetManager,
    AnkiAssetStateManager,
    get_addon_assets,
    has_newer_version,
    sync_assets,
)
from .clipboard import Clipboard, EmptyClipboard
from .dialog import (
    DISPLAY_STYLE,
    HighlighterConfig,
    HighlighterWizardState,
    HighlighterWizardStateJSONConverter,
    PartialPygmentsConfig,
    ask_for_highlighter_config,
)
from .field import set_up_style_import
from .html import PlainString
from .media import AnkiMediaInstaller
from .serialization import JSONObjectSerializer

addon_path = os.path.dirname(__file__)
ASSET_PREFIX = "_gch-"
DEFAULT_CSS_ASSETS = [
    "_gch-pygments-solarized.css",
]
VERSION_ASSET = "_gch-asset-version.txt"
GUARD = "Greg's Code Highlighter (Add-on 1527277801)"
CLASS_NAME = "gregs-code-highlighter"


def create_anki_asset_manager(css_assets: List[str], col: anki.collection.Collection):
    return AnkiAssetManager(
        AnkiMediaInstaller(ASSET_PREFIX, get_addon_assets(ASSET_PREFIX), col.media),
        css_assets,
        class_name=CLASS_NAME,
    )


def WizardStateManager(media):
    return AnkiAssetStateManager(
        media=media,
        path=Path(ASSET_PREFIX + "wizard-state.json"),
        serializer=JSONObjectSerializer(HighlighterWizardStateJSONConverter()),
        default=HighlighterWizardState(),
    )


def get_highlighter_config(
    parent, media, preselected: PartialPygmentsConfig
) -> Optional[HighlighterConfig]:
    """Gets the highlighter configuration from the user.

    - Shows the wizard to the user.
    - Handles state management of the wizard.
    - Respects configuration defaults.

    Args:
        parent: The parent widget.
        media: The media manager.
        preselected: The preselected configuration options.

    Returns:
        The highlighter configuration if the user accepted it, otherwise None.
    """
    with WizardStateManager(media) as wizard_state:
        highlighter_config, new_wizard_state = ask_for_highlighter_config(
            parent, preselected=preselected, state=wizard_state.get()
        )
        wizard_state.put(new_wizard_state)
    return highlighter_config


def get_qclipboard_or_empty() -> Clipboard:
    """Returns the QApplication clipboard or an empty clipboard."""
    return QApplication.clipboard() or EmptyClipboard()


def highlight_action(editor: aqt.editor.Editor) -> None:
    note: Optional[anki.notes.Note] = editor.note
    if note is None:
        showWarning(
            "You've run the code highlighter without selecting a note.\n"
            + "Select a note before running the code highlighter."
        )
        return None

    currentFieldNo = editor.currentField
    if currentFieldNo is None:
        showWarning(
            "You've run the code highlighter without selecting a field.\n"
            + "Select a note field before running the code highlighter."
        )
        return None

    parent = (aqt.mw and aqt.mw.app.activeWindow()) or aqt.mw
    mw = aqt.mw
    if not mw or not mw.col:
        # Should never happen
        return None
    media_manager: anki.media.MediaManager = mw.col.media

    block_style = config.get("block-style") or "display:flex; justify-content:center;"

    editor_interface = AnkiEditorInterface(editor.web, str(random.randint(0, 10000)))

    highlight(
        lambda preselected: get_highlighter_config(parent, media_manager, preselected),
        block_style,
        clipboard=get_qclipboard_or_empty(),
        editor=editor_interface,
        on_error=showWarning,
    )


# This is the side-effect free part of the highlight action.
def highlight(
    highlighter_config_factory: Callable[
        [PartialPygmentsConfig], Optional[HighlighterConfig]
    ],
    block_style: str,
    clipboard: Clipboard,
    editor: EditorInterface,
    on_error,
) -> None:
    """
    Highlights the selected or copied code snippet with a user configured
    highlighter and sets up necessary style imports (todo).
    """
    transform_selection(
        highlight=lambda code: highlight_selection(
            code,
            highlighter_config_factory,
            block_style,
            clipboard=clipboard,
            auto_detect_display_style=config.get(
                "auto-detect-display-style", default=True
            ),
        ),
        editor=editor,
        on_error=on_error,
        on_done=lambda: set_up_field_styles(editor, on_error),
    )


def set_up_field_styles(
    editor: EditorInterface, on_error: Callable[[str], Any]
) -> None:
    assets = DEFAULT_CSS_ASSETS

    def on_get(html_or_exception):
        if isinstance(html_or_exception, SelectionException):
            on_error(f"Failed to get field content: {str(html_or_exception)}")
            return None

        new_html = set_up_style_import(html_or_exception, assets, GUARD)

        def on_set(result_or_exception):
            if isinstance(result_or_exception, SelectionException):
                on_error(f"Failed to set field styles: {str(result_or_exception)}")

        editor.set_note_field(new_html, on_set)

    editor.get_note_field(on_get)


def _has_multiple_lines(code: str) -> bool:
    """Checks if the code snippet contains multiple lines."""
    return len(code.splitlines()) > 1


def _determine_preselected_highlighter_config(
    code: PlainString,
    auto_detect_display_style: bool = True,
) -> PartialPygmentsConfig:
    """Determines the preselected configuration based on the code content."""
    display_style = None
    if auto_detect_display_style:
        if _has_multiple_lines(code):
            display_style = DISPLAY_STYLE.BLOCK
    return PartialPygmentsConfig(display_style=display_style, language=None)


def highlight_selection(
    code: PlainString,
    highlighter_config_factory: Callable[
        [PartialPygmentsConfig], Optional[HighlighterConfig]
    ],
    block_style: str,
    clipboard: Clipboard,
    auto_detect_display_style: bool = True,
) -> Optional[bs4.Tag]:
    """Highlights the selected or copied code snippet with a user configured highlighter.

    This is like `highlight` but with the code provided upfront without any
    selection transformation logic.
    """
    if len(code) == 0:
        code = PlainString(clipboard.text())

    preselected_highlighter_config = _determine_preselected_highlighter_config(
        code,
        auto_detect_display_style=auto_detect_display_style,
    )

    highlighter_config = highlighter_config_factory(preselected_highlighter_config)
    if not highlighter_config:
        return None

    display_style = highlighter_config.display_style
    html_style = (
        pygments_highlighter.create_inline_style()
        if display_style == DISPLAY_STYLE.INLINE
        else pygments_highlighter.create_block_style(block_style)
    )

    return pygments_highlighter.highlight(
        code, language=highlighter_config.language, style=html_style
    )


def get_shortcut() -> str:
    """
    Gets the keyboard shortcut for the highlighting action.

    :rtype str: The keyboard shortcut, e.g., "ctrl+o".
    """
    return config.get("shortcut") or "ctrl+o"


def on_editor_shortcuts_init(
    _shortcuts: List[Tuple], editor: aqt.editor.Editor
) -> None:
    aqt.qt.QShortcut(  # type: ignore
        aqt.qt.QKeySequence(get_shortcut()),  # type: ignore
        editor.widget,
        activated=lambda: highlight_action(editor),
    )


def on_editor_buttons_init(buttons: List, editor: aqt.editor.Editor) -> None:
    action_button = editor.addButton(
        icon=os.path.join(addon_path, "icons", "icon.png"),
        cmd="highlight",
        func=lambda editor: highlight_action(editor),
        tip=f"Highlight current text selection (v2, {get_shortcut()}).",
        # Skip label, because we already provide an icon.
    )
    buttons.append(action_button)


def setup_menu() -> None:
    # Manipulating assets should not be a part of a normal flow.
    # Let’s leave it out of the supported surface.
    dev_mode = config.get("dev-mode") or False
    if not dev_mode:
        return

    main_window = mw

    if not main_window or not main_window.col:
        # For some reason the main window is not initialized yet. Let's print
        # an error message.
        showWarning(
            "Code Highlighter plugin tried to initialize, "
            + "but couldn't find the main window.\n"
            + "Please report it to the author at "
            + "https://github.com/gregorias/anki-code-highlighter/issues/new."
        )
        return None

    col = main_window.col

    main_window.form.menuTools.addSection("Code Highlighter")

    def refresh() -> None:
        # Create AnkiAssetManager inside actions and not in setup_menu,
        # because:
        # 1. setup_menu runs in main_window_did_init, which may happen before
        #    profile load
        #    (https://github.com/gregorias/anki-code-highlighter/issues/22).
        # 2. create_anki_asset_manager requires a profile to be loaded.
        anki_asset_manager = create_anki_asset_manager(DEFAULT_CSS_ASSETS, col)
        anki_asset_manager.delete_assets()
        anki_asset_manager.install_assets()

    def delete() -> None:
        anki_asset_manager = create_anki_asset_manager(DEFAULT_CSS_ASSETS, col)
        anki_asset_manager.delete_assets()

    a = aqt.qt.QAction("Refresh Greg’s Code Highlighter Assets", main_window)  # type: ignore
    a.triggered.connect(refresh)
    main_window.form.menuTools.addAction(a)
    a = aqt.qt.QAction("Delete Greg’s Code Highlighter Assets", main_window, triggered=delete)  # type: ignore
    a.triggered.connect(delete)
    main_window.form.menuTools.addAction(a)


def load_mw_and_sync():
    main_window = mw
    if not main_window or not main_window.col:
        # For some reason the main window is not initialized yet. Let's print
        # an error message.
        showWarning(
            "Code Highlighter plugin tried to initialize, "
            + "but couldn't find the main window.\n"
            + "Please report it to the author at "
            + "https://github.com/gregorias/anki-code-highlighter/issues/new."
        )
        return None

    anki_asset_manager = create_anki_asset_manager(DEFAULT_CSS_ASSETS, main_window.col)
    sync_assets(
        partial(has_newer_version, main_window.col.media, VERSION_ASSET),
        anki_asset_manager,
    )


def main():
    gui_hooks.profile_did_open.append(load_mw_and_sync)
    gui_hooks.main_window_did_init.append(setup_menu)
    gui_hooks.editor_did_init_shortcuts.append(on_editor_shortcuts_init)
    gui_hooks.editor_did_init_buttons.append(on_editor_buttons_init)
