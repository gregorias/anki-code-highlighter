"""The implementation of the code highlighter plugin."""

import os.path
import random
import sys
from functools import partial
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

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
import anki.models
import anki.notes

from . import pygments_highlighter
from .ankieditorextra import AnkiEditorInterface, EditorInterface, transform_selection
from .assets import (
    AnkiAssetManager,
    AnkiAssetStateManager,
    has_newer_version,
    sync_assets,
)
from .clipboard import Clipboard, EmptyClipboard
from .dialog import (
    DISPLAY_STYLE,
    HighlighterConfig,
    HighlighterWizardState,
    HighlighterWizardStateJSONConverter,
    ask_for_highlighter_config,
)
from .html import PlainString
from .serialization import JSONObjectSerializer

addon_path = os.path.dirname(__file__)
ASSET_PREFIX = "_ch-"
DEFAULT_CSS_ASSETS = [
    "_ch-pygments-solarized.css",
    "_ch-hljs-solarized.css",
]
# We can’t just load with <script src="foo.js">, because it causes flicker
# (https://github.com/gregorias/anki-code-highlighter/issues/94).
#
# However, dynamic import makes the flicker worse on mobile.
HLJS_SCRIPT = """
var hljs;
if (document.currentScript.closest('.mobile')) {
  const script = document.createElement('script');
  script.src = '_ch-highlight.js';
  script.type = 'text/javascript';
  document.head.appendChild(script);
} else if (!hljs) {
  import("/_ch-highlight-export.js").then(moduleObj => {
    globalThis.hljs = moduleObj.hljs;
    globalThis.hljs.configure({
      cssSelector: 'pre code[class^="language-"]:not([data-highlighted="yes"])',
    });
    globalThis.hljs.highlightAll();

  });
} else {
  globalThis.hljs.configure({
    cssSelector: 'pre code[class^="language-"]:not([data-highlighted="yes"])',
  });
  globalThis.hljs.highlightAll();
}
"""
VERSION_ASSET = "_ch-asset-version.txt"
GUARD = "Anki Code Highlighter (Addon 112228974)"
CLASS_NAME = "anki-code-highlighter"

Config = Dict[str, str]


def config() -> Optional[Config]:
    if not aqt.mw:
        return None
    return aqt.mw.addonManager.getConfig(__name__)


def get_config(key: str) -> Optional[str]:
    config_snapshot = config()
    if not config_snapshot:
        return None
    return config_snapshot.get(key)


def css_files() -> List[str]:
    """
    A list of configured css files to use for styling.

    :rtype List[str]
    """
    config_css_files = get_config("css-files") or DEFAULT_CSS_ASSETS
    print(repr(config_css_files))

    if not (
        isinstance(config_css_files, list)
        and all([isinstance(e, str) for e in config_css_files])
    ):
        showWarning(
            "The configured css-files for the code highlighter plugin "
            + f"should be a list of CSS files but got {repr(config_css_files)}.\n"
            + "Fix the plugin's configuration."
        )
        return DEFAULT_CSS_ASSETS

    return config_css_files


def create_anki_asset_manager(css_assets: List[str], col: anki.collection.Collection):
    return AnkiAssetManager(
        partial(transform_templates, col.models),
        col.media,
        ASSET_PREFIX,
        css_assets,
        script_elements=[HLJS_SCRIPT],
        guard=GUARD,
        class_name=CLASS_NAME,
    )


def WizardStateManager(media):
    return AnkiAssetStateManager(
        media=media,
        path=Path(ASSET_PREFIX + "wizard-state.json"),
        serializer=JSONObjectSerializer(HighlighterWizardStateJSONConverter()),
        default=HighlighterWizardState(),
    )


def get_highlighter_config(parent, media) -> Optional[HighlighterConfig]:
    """Gets the highlighter configuration from the user.

    - Shows the wizard to the user.
    - Handles state management of the wizard.
    - Respects configuration defaults.

    Args:
        parent

    Returns:
        The highlighter configuration if the user accepted it, otherwise None.
    """
    with WizardStateManager(media) as wizard_state:
        highlighter_config, new_wizard_state = ask_for_highlighter_config(
            parent, wizard_state.get()
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

    block_style = get_config("block-style") or "display:flex; justify-content:center;"

    editor_interface = AnkiEditorInterface(editor.web, str(random.randint(0, 10000)))

    highlight(
        lambda: get_highlighter_config(parent, media_manager),
        block_style,
        clipboard=get_qclipboard_or_empty(),
        editor=editor_interface,
        on_error=showWarning,
    )


# This is the side-effect free part of the highlight action.
def highlight(
    highlighter_config_factory: Callable[[], Optional[HighlighterConfig]],
    block_style: str,
    clipboard: Clipboard,
    editor: EditorInterface,
    on_error,
) -> None:
    """
    Highlights the selected or copied code snippet with a user configured
    highlighter.
    """
    transform_selection(
        highlight=lambda code: highlight_selection(
            code, highlighter_config_factory, block_style, clipboard=clipboard
        ),
        editor=editor,
        onError=on_error,
    )


def highlight_selection(
    code: PlainString,
    highlighter_config_factory: Callable[[], Optional[HighlighterConfig]],
    block_style: str,
    clipboard: Clipboard,
) -> Optional[bs4.Tag]:
    """
    Highlights the selected or copied code snippet with a user configured
    highlighter.

    This is like `highlight` but with the code provided upfront without any
    selection transformation logic.
    """
    if len(code) == 0:
        code = PlainString(clipboard.text())

    highlighter_config = highlighter_config_factory()
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

    :rtype str: The keyboard shortcut, e.g., "ctrl+'".
    """
    return get_config("shortcut") or "ctrl+'"


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
        tip=f"Highlight current text selection ({get_shortcut()}).",
        # Skip label, because we already provide an icon.
    )
    buttons.append(action_button)


def transform_templates(models: anki.models.ModelManager, modify: Callable[[str], str]):
    """Transforms all card templates with modify."""
    for model in models.all():
        for tmpl in model["tmpls"]:
            tmpl["afmt"] = modify(tmpl["afmt"])
            tmpl["qfmt"] = modify(tmpl["qfmt"])
        models.save(model)


def setup_menu() -> None:
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
        anki_asset_manager = create_anki_asset_manager(css_files(), col)
        anki_asset_manager.delete_assets()
        anki_asset_manager.install_assets()

    def delete() -> None:
        anki_asset_manager = create_anki_asset_manager(css_files(), col)
        anki_asset_manager.delete_assets()

    a = aqt.qt.QAction("Refresh Code Highlighter Assets", main_window)  # type: ignore
    a.triggered.connect(refresh)
    main_window.form.menuTools.addAction(a)
    a = aqt.qt.QAction("Delete Code Highlighter Assets", main_window, triggered=delete)  # type: ignore
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

    anki_asset_manager = create_anki_asset_manager(css_files(), main_window.col)
    sync_assets(
        partial(has_newer_version, main_window.col.media, VERSION_ASSET),
        anki_asset_manager,
    )


def main():
    gui_hooks.profile_did_open.append(load_mw_and_sync)
    gui_hooks.main_window_did_init.append(setup_menu)
    gui_hooks.editor_did_init_shortcuts.append(on_editor_shortcuts_init)
    gui_hooks.editor_did_init_buttons.append(on_editor_buttons_init)
