# -*- coding: utf-8 -*-
"""The implementation of the word hyphenator plugin."""
import os.path
import pathlib
import random
import re
from typing import Generator, List, Optional

from anki import hooks  # type: ignore
import aqt  # type: ignore
from aqt import mw  # type: ignore
from aqt import gui_hooks  # type: ignore
from aqt.utils import showWarning  # type: ignore
import bs4  # type: ignore
from bs4 import BeautifulSoup, NavigableString  # type: ignore

from PyQt5.QtWidgets import QInputDialog  # type: ignore

addon_path = os.path.dirname(__file__)
config = aqt.mw and aqt.mw.addonManager.getConfig(__name__)


def get_config(key: str, default):
    return (config and config.get(key, default)) or default


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


def highlight_inline_action(editor: aqt.editor.Editor) -> None:
    editor.web.eval(f"""wrap('<code class="language-todo">', '</code>');""")


def on_editor_buttons_init(buttons: List[str],
                           editor: aqt.editor.Editor) -> None:
    shortcut = "ctrl+'"
    icon_path = os.path.join(addon_path, "icons", "silent hyphen.png")
    css = editor.addButton(icon=None,
                           cmd="highlight-block",
                           func=highlight_block_action,
                           tip="Highlight code ({})".format(shortcut),
                           label="Highligh Block",
                           keys=shortcut)
    buttons.append(css)

    shortcut = "ctrl+shift+\""
    css = editor.addButton(icon=None,
                           cmd="highlight-inline",
                           func=highlight_inline_action,
                           tip="Highlight code ({})".format(shortcut),
                           label="Highligh Inline",
                           keys=shortcut)
    buttons.append(css)


def anki_media_directory() -> pathlib.Path:
    return pathlib.Path(mw.col.media.dir())


def codehighlighter_assets_directory() -> pathlib.Path:
    return pathlib.Path(addon_path) / 'assets'


def list_my_assets(dir: pathlib.Path) -> List[str]:
    return [f for f in os.listdir(dir) if f.startswith("_ch-")]


def delete_media_assets():
    print("Deleting media assets")
    my_assets = list_my_assets(anki_media_directory())
    mw.col.media.trash_files(my_assets)


def install_media_assets():
    print("Install media assets")
    codehighlighter_assets_dir = codehighlighter_assets_directory()
    my_assets = list_my_assets(codehighlighter_assets_dir)
    for asset in my_assets:
        mw.col.media.add_file(codehighlighter_assets_dir / asset)


def setup_menu():
    mw.form.menuTools.addSection("Code Highlighter")
    mw.form.menuTools.addAction(
        aqt.qt.QAction("Install Media Assets",
                       mw,
                       triggered=install_media_assets))
    mw.form.menuTools.addAction(
        aqt.qt.QAction("Delete Media Assets",
                       mw,
                       triggered=delete_media_assets))


setup_menu()
gui_hooks.editor_did_init_buttons.append(on_editor_buttons_init)