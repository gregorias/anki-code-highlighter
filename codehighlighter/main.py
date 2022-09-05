# -*- coding: utf-8 -*-
"""The implementation of the code highlighter plugin."""
from functools import partial
import os.path
import pathlib
import random
from typing import Callable, Generator, List, Optional, Tuple

import aqt  # type: ignore
from aqt import mw
from aqt import gui_hooks
from aqt.utils import showWarning  # type: ignore
import bs4  # type: ignore
from bs4 import BeautifulSoup, NavigableString
from PyQt5.QtWidgets import QInputDialog  # type: ignore

from .assets import AnkiAssetManager, sync_assets
from .bs4extra import encode_soup
from .highlighter import format_code

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
                            CSS_ASSETS, JS_ASSETS, VERSION_ASSET, CLASS_NAME)


def ask_for_language(parent=None) -> Optional[str]:
    parent = parent or (aqt.mw and aqt.mw.app.activeWindow()) or aqt.mw
    lang, ok = QInputDialog.getText(
        parent, 'Enter language',
        'Provide language for the snippet (e.g. cpp)')
    return ok and lang


def find_tags_and_replace(html: str, replace: Callable[[str], bs4.Tag],
                          id: str):
    soup = BeautifulSoup(html, features='html.parser')
    for div_node in soup.find_all(id=id):
        div_node.replace_with(replace(div_node.decode_contents()))
    return encode_soup(soup)


def highlight_block_action(editor: aqt.editor.Editor) -> None:
    currentFieldNo = editor.currentField
    if currentFieldNo is None:
        showWarning(
            "You've run the code highlighter without selecting a field.\n" +
            "Please select a note field before running the code highlighter.")
        return None

    random_id = 'anki-code-highlighter-todo-' + str(random.randint(0, 10000))
    editor.web.eval(f"""wrap('<div id="{random_id}">', '</div>');""")
    language = ask_for_language(parent=None)
    if language:
        language = 'language-' + language
    else:
        language = 'nohighlight'

    note = editor.note
    if not note:
        showWarning(
            "The note has disappered before the code highlighter could act.\n"
            + "Please try again.")
        return None
    field = note.fields[currentFieldNo]
    note.fields[currentFieldNo] = find_tags_and_replace(field,
                                                        partial(
                                                            format_code,
                                                            language),
                                                        id=random_id)

    # That's how aqt.editor.onHtmlEdit saves cards.
    # It's better than `editor.mw.reset()`, because the latter loses focus.
    # Calls like editor.mw.reset() or editor.loadNote() are necessary to save
    # HTML changes.
    if not editor.addMode:
        note.flush()
    editor.loadNoteKeepingFocus()


def on_editor_shortcuts_init(shortcuts: List[Tuple],
                             editor: aqt.editor.Editor) -> None:
    shortcut = get_config("shortcut", "ctrl+'")
    aqt.qt.QShortcut(  # type: ignore
        aqt.qt.QKeySequence(shortcut),  # type: ignore
        editor.widget,
        activated=lambda: highlight_block_action(editor))


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
    sync_assets(anki_asset_manager)


gui_hooks.profile_did_open.append(load_mw_and_sync)
gui_hooks.main_window_did_init.append(setup_menu)
gui_hooks.editor_did_init_shortcuts.append(on_editor_shortcuts_init)
