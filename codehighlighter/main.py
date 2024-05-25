"""The implementation of the code highlighter plugin."""
import os.path
import sys
from functools import partial
from typing import Callable, Dict, List, Optional, Tuple

import aqt
import bs4
from aqt import gui_hooks, mw
from aqt.qt import QApplication
from aqt.utils import showWarning

sys.path.append(os.path.dirname(__file__))

import anki  # type: ignore

from . import dialog, hljs, pygments_highlighter
from .ankieditorextra import transform_selection
from .assets import (
    AnkiAssetManager,
    AnkiAssetStateManager,
    has_newer_version,
    sync_assets,
)
from .dialog import (
    DISPLAY_STYLE,
    HIGHLIGHT_METHOD,
    HighlighterConfig,
    HighlighterWizardState,
    HighlighterWizardStateJSONConverter,
    HljsConfig,
    ask_for_highlight_method,
    ask_for_highlighter_config,
)
from .format import Clipboard, EmptyClipboard, format_selected_code
from .serialization import JSONObjectSerializer

addon_path = os.path.dirname(__file__)
ASSET_PREFIX = '_ch-'
DEFAULT_CSS_ASSETS = [
    "_ch-pygments-solarized.css",
    "_ch-hljs-solarized.css",
]
JS_ASSETS = ["_ch-highlight.js", "_ch-my-highlight.js"]
VERSION_ASSET = '_ch-asset-version.txt'
GUARD = 'Anki Code Highlighter (Addon 112228974)'
CLASS_NAME = 'anki-code-highlighter'

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


def get_default_highlighter(config: Config) -> Optional[HIGHLIGHT_METHOD]:
    default_highlighter = config.get("default-highlighter")
    if default_highlighter is None:
        return None
    return dialog.highlight_method_name_to_enum(default_highlighter)


def css_files() -> List[str]:
    """
    A list of configured css files to use for styling.

    :rtype List[str]
    """
    config_css_files = get_config('css-files') or DEFAULT_CSS_ASSETS
    print(repr(config_css_files))

    if not (isinstance(config_css_files, list)
            and all([isinstance(e, str) for e in config_css_files])):
        showWarning(
            "The configured css-files for the code highlighter plugin " +
            f"should be a list of CSS files but got {repr(config_css_files)}.\n"
            + "Fix the plugin's configuration.")
        return DEFAULT_CSS_ASSETS

    return config_css_files


def create_anki_asset_manager(css_assets: List[str],
                              col: anki.collection.Collection):
    return AnkiAssetManager(partial(transform_templates, col.models),
                            col.media,
                            ASSET_PREFIX,
                            css_assets,
                            JS_ASSETS,
                            guard=GUARD,
                            class_name=CLASS_NAME)


WIZARD_STATE = HighlighterWizardState()


def WizardStateManager(media):
    return AnkiAssetStateManager(media=media,
                                 path=ASSET_PREFIX + "wizard-state.json",
                                 serializer=JSONObjectSerializer(
                                     HighlighterWizardStateJSONConverter()),
                                 default=HighlighterWizardState())


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
    config_dict = config()
    default_highlighter = config_dict and get_default_highlighter(config_dict)

    def get_highlighter(
            current: Optional[HIGHLIGHT_METHOD]) -> Optional[HIGHLIGHT_METHOD]:
        if default_highlighter:
            return default_highlighter
        else:
            return ask_for_highlight_method(parent, current)

    with WizardStateManager(media) as wizard_state:
        highlighter_config, new_wizard_state = ask_for_highlighter_config(
            parent, wizard_state.get(), get_highlighter=get_highlighter)
        wizard_state.put(new_wizard_state)
    return highlighter_config


def get_qclipboard_or_empty() -> Clipboard:
    """Returns the QApplication clipboard or an empty clipboard."""
    return QApplication.clipboard() or EmptyClipboard()


def highlight_action(editor: aqt.editor.Editor) -> None:
    note: Optional[anki.notes.Note] = editor.note
    currentFieldNo = editor.currentField
    if note is None:
        showWarning(
            "You've run the code highlighter without selecting a note.\n" +
            "Select a note before running the code highlighter.")
        return None
    if currentFieldNo is None:
        showWarning(
            "You've run the code highlighter without selecting a field.\n" +
            "Select a note field before running the code highlighter.")
        return None

    def highlight(code: str) -> Optional[bs4.Tag]:
        parent = (aqt.mw and aqt.mw.app.activeWindow()) or aqt.mw
        mw = aqt.mw
        if not mw:
            # Should never happen
            return None
        highlighter_config: Optional[
            HighlighterConfig] = get_highlighter_config(parent, mw.col.media)
        if not highlighter_config:
            return None

        block_style = (get_config("block-style")
                       or "display:flex; justify-content:center;")
        if isinstance(highlighter_config, HljsConfig):
            return hljs.highlight(code,
                                  language=highlighter_config.language,
                                  block_style=block_style)
        else:
            display_style = highlighter_config.display_style
            html_style = (pygments_highlighter.create_inline_style()
                          if display_style == DISPLAY_STYLE.INLINE else
                          pygments_highlighter.create_block_style(block_style))

            return pygments_highlighter.highlight(
                code, language=highlighter_config.language, style=html_style)

    def format(code: str) -> Optional[bs4.Tag]:
        return format_selected_code(code,
                                    highlight=highlight,
                                    clipboard=get_qclipboard_or_empty())

    transform_selection(editor, note, currentFieldNo, format, showWarning)


def get_shortcut() -> str:
    """
    Gets the keyboard shortcut for the highlighting action.

    :rtype str: The keyboard shortcut, e.g., "ctrl+'".
    """
    return get_config("shortcut") or "ctrl+'"


def on_editor_shortcuts_init(shortcuts: List[Tuple],
                             editor: aqt.editor.Editor) -> None:
    aqt.qt.QShortcut(  # type: ignore
        aqt.qt.QKeySequence(get_shortcut()),  # type: ignore
        editor.widget,
        activated=lambda: highlight_action(editor))


def on_editor_buttons_init(buttons: List, editor: aqt.editor.Editor) -> None:
    action_button = editor.addButton(
        icon=os.path.join(addon_path, "icons", "icon.png"),
        cmd="highlight",
        func=lambda editor: highlight_action(editor),
        tip=f"Highlight current text selection ({get_shortcut()}).",
        # Skip label, because we already provide an icon.
    )
    buttons.append(action_button)


def transform_templates(models: anki.models.ModelManager,
                        modify: Callable[[str], str]):
    """Transforms all card templates with modify."""
    for model in models.all():
        for tmpl in model['tmpls']:
            tmpl['afmt'] = modify(tmpl['afmt'])
            tmpl['qfmt'] = modify(tmpl['qfmt'])
        models.save(model)


def setup_menu() -> None:
    if not mw:
        # For some reason the main window is not initialized yet. Let's print
        # an error message.
        showWarning(
            "Code Highlighter plugin tried to initialize, " +
            "but couldn't find the main window.\n" +
            "Please report it to the author at " +
            "https://github.com/gregorias/anki-code-highlighter/issues/new.")
        return None
    main_window = mw
    main_window.form.menuTools.addSection("Code Highlighter")

    def refresh() -> None:
        # Create AnkiAssetManager inside actions and not in setup_menu,
        # because:
        # 1. setup_menu runs in main_window_did_init, which may happen before
        #    profile load
        #    (https://github.com/gregorias/anki-code-highlighter/issues/22).
        # 2. create_anki_asset_manager requires a profile to be loaded.
        anki_asset_manager = create_anki_asset_manager(css_files(),
                                                       main_window.col)
        anki_asset_manager.delete_assets()
        anki_asset_manager.install_assets()

    def delete() -> None:
        anki_asset_manager = create_anki_asset_manager(css_files(),
                                                       main_window.col)
        anki_asset_manager.delete_assets()

    # I'm getting type errors below but the code works, so let's ignore.
    main_window.form.menuTools.addAction(
        aqt.qt.QAction("Refresh Code Highlighter Assets",
                       main_window,
                       triggered=refresh))  # type: ignore
    main_window.form.menuTools.addAction(
        aqt.qt.QAction("Delete Code Highlighter Assets",
                       main_window,
                       triggered=delete))  # type: ignore


def load_mw_and_sync():
    main_window = mw
    if not main_window:
        # For some reason the main window is not initialized yet. Let's print
        # an error message.
        showWarning(
            "Code Highlighter plugin tried to initialize, " +
            "but couldn't find the main window.\n" +
            "Please report it to the author at " +
            "https://github.com/gregorias/anki-code-highlighter/issues/new.")
        return None
    anki_asset_manager = create_anki_asset_manager(css_files(),
                                                   main_window.col)
    sync_assets(
        partial(has_newer_version, main_window.col.media, VERSION_ASSET),
        anki_asset_manager)


gui_hooks.profile_did_open.append(load_mw_and_sync)
gui_hooks.main_window_did_init.append(setup_menu)
gui_hooks.editor_did_init_shortcuts.append(on_editor_shortcuts_init)
gui_hooks.editor_did_init_buttons.append(on_editor_buttons_init)
