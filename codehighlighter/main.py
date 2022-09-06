# -*- coding: utf-8 -*-
"""The implementation of the code highlighter plugin."""
from functools import partial
import os.path
import pathlib
import random
from typing import Callable, Generator, List, Optional, Tuple, Union

import aqt  # type: ignore
from aqt import mw
from aqt import gui_hooks
from aqt.utils import showWarning  # type: ignore
import bs4  # type: ignore
from bs4 import BeautifulSoup, NavigableString
from PyQt5.QtWidgets import QInputDialog  # type: ignore

from .ankieditorextra import transform_selection
from .assets import AnkiAssetManager, has_newer_version, sync_assets
from .bs4extra import encode_soup
from .highlighter import format_code, DISPLAY_STYLE, format_code_pygments

import anki  # type: ignore

addon_path = os.path.dirname(__file__)
config = aqt.mw and aqt.mw.addonManager.getConfig(__name__)
ASSET_PREFIX = '_ch-'
CSS_ASSETS = [
    "_ch-pygments-solarized.old.css",
    "_ch-pygments-solarized.css",
    "_ch-hljs-solarized.css",
]
JS_ASSETS = ["_ch-my-highlight.js"]
VERSION_ASSET = '_ch-asset-version.txt'
CLASS_NAME = 'anki-code-highlighter'


def get_config(key: str, default):
    if config:
        return config.get(key, default)
    else:
        return default


def create_anki_asset_manager(col: anki.collection.Collection):
    return AnkiAssetManager(partial(transform_templates,
                                    col.models), col.media, ASSET_PREFIX,
                            CSS_ASSETS, JS_ASSETS, CLASS_NAME)


def ask_for_language(parent=None) -> Optional[str]:
    parent = parent or (aqt.mw and aqt.mw.app.activeWindow()) or aqt.mw
    lang, ok = QInputDialog.getText(
        parent, 'Enter language',
        'Provide language for the snippet (e.g. cpp)')
    return ok and lang


def highlight_block_action(editor: aqt.editor.Editor) -> None:
    note = editor.note
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

    def show_dialogs() -> str:
        language = ask_for_language(parent=None)
        return 'language-' + language if language else 'nohighlight'

    transform_selection(editor, note, currentFieldNo, show_dialogs,
                        format_code)


def highlight_action(editor: aqt.editor.Editor) -> None:
    note = editor.note
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

    def show_dialogs() -> Optional[Tuple[str, DISPLAY_STYLE, str]]:
        parent = (aqt.mw and aqt.mw.app.activeWindow()) or aqt.mw
        method, ok = QInputDialog.getItem(parent, 'Highlighting method',
                                          'Select a highlighting method',
                                          ['highlight.js', 'pygments'])
        if not ok or not method:
            return None
        if method == 'pygments':
            display_style, ok = QInputDialog.getItem(parent, 'Display style',
                                                     'Select a display style',
                                                     ['block', 'inline'])
            if not ok:
                return None
            display_style = (DISPLAY_STYLE.BLOCK if display_style == 'block'
                             else DISPLAY_STYLE.INLINE)
        else:
            display_style = DISPLAY_STYLE.BLOCK

        language = ask_for_language(parent=None)
        if not language:
            return None
        return method, display_style, language

    def format(args: Optional[Tuple[str, DISPLAY_STYLE, str]],
               code) -> Union[bs4.Tag, bs4.BeautifulSoup]:
        if not args:
            return bs4.BeautifulSoup(code, features='html.parser')
        method, display_style, language = args
        if method == 'highlight.js':
            return format_code(language, code)
        elif method == 'pygments':
            return format_code_pygments(language, display_style, code)
        else:
            return bs4.BeautifulSoup(code, features='html.parser')

    transform_selection(editor, note, currentFieldNo, show_dialogs, format)


def on_editor_shortcuts_init(shortcuts: List[Tuple],
                             editor: aqt.editor.Editor) -> None:
    shortcut = get_config("shortcut", "ctrl+'")
    aqt.qt.QShortcut(  # type: ignore
        aqt.qt.QKeySequence(shortcut),  # type: ignore
        editor.widget,
        activated=lambda: highlight_block_action(editor))
    for shortcut in ['ctrl+"', 'ctrl+shift+\'', 'ctrl+;']:
        aqt.qt.QShortcut(  # type: ignore
            aqt.qt.QKeySequence(shortcut),  # type: ignore
            editor.widget,
            activated=lambda: highlight_action(editor))


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
    anki_asset_manager = create_anki_asset_manager(main_window.col)

    def refresh() -> None:
        anki_asset_manager.delete_assets()
        anki_asset_manager.install_assets()

    def delete() -> None:
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
    anki_asset_manager = create_anki_asset_manager(main_window.col)
    sync_assets(
        partial(has_newer_version, main_window.col.media, VERSION_ASSET),
        anki_asset_manager)


gui_hooks.profile_did_open.append(load_mw_and_sync)
gui_hooks.main_window_did_init.append(setup_menu)
gui_hooks.editor_did_init_shortcuts.append(on_editor_shortcuts_init)
