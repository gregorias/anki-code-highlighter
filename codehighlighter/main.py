# -*- coding: utf-8 -*-
"""The implementation of the word hyphenator plugin."""
import os.path
import pathlib
import random
import re
from typing import Callable, Generator, List, Optional, Tuple

import aqt  # type: ignore
from aqt import mw  # type: ignore
from aqt import gui_hooks  # type: ignore
from aqt.utils import showWarning  # type: ignore
import bs4  # type: ignore
from bs4 import BeautifulSoup, NavigableString  # type: ignore
from PyQt5.QtWidgets import QInputDialog  # type: ignore

from .assets import AnkiAssetManager, sync_assets

addon_path = os.path.dirname(__file__)
config = aqt.mw and aqt.mw.addonManager.getConfig(__name__)


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

    field = editor.note.fields[currentFieldNo]
    editor.note.fields[currentFieldNo] = format_code(random_id, language,
                                                     field)
    # That's how aqt.editor.onHtmlEdit saves cards.
    # It's better than `editor.mw.reset()`, because the latter loses focus.
    # Calls like editor.mw.reset() or editor.loadNote() are necessary to save
    # HTML changes.
    if not editor.addMode:
        editor.note.flush()
    editor.loadNoteKeepingFocus()


def on_editor_shortcuts_init(shortcuts: List[Tuple],
                             editor: aqt.editor.Editor) -> None:
    shortcut = get_config("shortcut", "ctrl+'")
    aqt.qt.QShortcut(  # type: ignore
        aqt.qt.QKeySequence(shortcut),  # type: ignore
        editor.widget,
        activated=lambda: highlight_block_action(editor))


def modify_templates(modify: Callable[[str], str]) -> None:
    """Modifies all card templates with modify."""
    for model in mw.col.models.all():
        for tmpl in model['tmpls']:
            tmpl['afmt'] = modify(tmpl['afmt'])
            tmpl['qfmt'] = modify(tmpl['qfmt'])
        mw.col.models.save(model)


def setup_menu() -> None:
    global anki_asset_manager
    mw.form.menuTools.addSection("Code Highlighter")

    def refresh() -> None:
        anki_asset_manager.delete_assets()
        anki_asset_manager.install_assets()

    def delete() -> None:
        anki_asset_manager.delete_assets()

    mw.form.menuTools.addAction(
        aqt.qt.QAction("Refresh Code Highlighter Assets",
                       mw,
                       triggered=refresh))
    mw.form.menuTools.addAction(
        aqt.qt.QAction("Delete Code Highlighter Assets", mw, triggered=delete))


anki_asset_manager = AnkiAssetManager(modify_templates)

gui_hooks.main_window_did_init.append(lambda: sync_assets(anki_asset_manager))
gui_hooks.main_window_did_init.append(setup_menu)
gui_hooks.editor_did_init_shortcuts.append(on_editor_shortcuts_init)
