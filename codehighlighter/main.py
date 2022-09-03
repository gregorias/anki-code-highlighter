# -*- coding: utf-8 -*-
"""The implementation of the code highlighter plugin."""
from functools import partial
import os.path
import pathlib
import random
import re
from typing import Callable, Generator, List, Optional, Tuple

import aqt
from aqt import mw
from aqt import gui_hooks
from aqt.utils import showWarning
import bs4
from bs4 import BeautifulSoup, NavigableString
from PyQt5.QtWidgets import QInputDialog  # type: ignore

from .assets import AnkiAssetManager, sync_assets
import anki

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


def ask_for_language(parent=None) -> Optional[str]:
    parent = parent or (aqt.mw and aqt.mw.app.activeWindow()) or aqt.mw
    lang, ok = QInputDialog.getText(
        parent, 'Enter language',
        'Provide language for the snippet (e.g. cpp)')
    return ok and lang


def replace_br(element: bs4.PageElement) -> None:
    if isinstance(element, bs4.Tag) and element.name == 'br':
        element.replace_with('\n')


def walk(soup: bs4.BeautifulSoup, func):

    class DfsStack:

        def __init__(self, initial_nodes):
            self.nodes = list(initial_nodes)

        def __iter__(self):
            return self

        def __next__(self):
            if self.nodes:
                top = self.nodes[-1]
                self.nodes.pop()
                return top
            else:
                raise StopIteration()

        def send(self, new_nodes: List[bs4.PageElement]):
            self.nodes.extend(list(new_nodes))

    dfs_stack = DfsStack(soup.children)
    for node in dfs_stack:
        maybe_more_nodes = func(node)
        if maybe_more_nodes:
            dfs_stack.send(maybe_more_nodes)


def format_code(random_id: str, language: str, html: str) -> str:
    """Formats the just create code element.

    Returns:
        An HTML5-encoded string.
    """
    soup = BeautifulSoup(html, features='html.parser')
    for code_node in soup.find_all(id=random_id):
        del code_node['id']
        code_node['class'] = [language]
        walk(code_node, replace_br)
    return str(soup.encode(formatter='html5'), 'utf8')


def highlight_block_action(editor: aqt.editor.Editor) -> None:
    currentFieldNo = editor.currentField
    if currentFieldNo is None:
        showWarning(
            "You've run the code highlighter without selecting a field.\n" +
            "Please select a note field before running the code highlighter.")
        return None

    random_id = 'anki-code-highlighter-todo-' + str(random.randint(0, 10000))
    editor.web.eval(
        f"""wrap('<pre style="display:flex; justify-content:center;"><code id="{random_id}">', '</code></pre>');"""
    )
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
    note.fields[currentFieldNo] = format_code(random_id, language, field)
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

    def refresh() -> None:
        anki_asset_manager = AnkiAssetManager(
            partial(transform_templates,
                    main_window.col.models), main_window.col, ASSET_PREFIX,
            CSS_ASSETS, JS_ASSETS, VERSION_ASSET, CLASS_NAME)
        anki_asset_manager.delete_assets()
        anki_asset_manager.install_assets()

    def delete() -> None:
        anki_asset_manager = AnkiAssetManager(
            partial(transform_templates,
                    main_window.col.models), main_window.col, ASSET_PREFIX,
            CSS_ASSETS, JS_ASSETS, VERSION_ASSET, CLASS_NAME)
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
    anki_asset_manager = AnkiAssetManager(
        partial(transform_templates, main_window.col.models), main_window.col,
        ASSET_PREFIX, CSS_ASSETS, JS_ASSETS, VERSION_ASSET, CLASS_NAME)
    sync_assets(anki_asset_manager)


gui_hooks.profile_did_open.append(load_mw_and_sync)
gui_hooks.main_window_did_init.append(setup_menu)
gui_hooks.editor_did_init_shortcuts.append(on_editor_shortcuts_init)
