# -*- coding: utf-8 -*-
"""The implementation of the code highlighter plugin."""
from dataclasses import dataclass
import enum
from enum import Enum
from functools import partial
import os.path
import pathlib
import random
import sys
from typing import Callable, Dict, Generator, List, Optional, Tuple, Union

import aqt  # type: ignore
from aqt import mw
from aqt import gui_hooks
from aqt.utils import showWarning  # type: ignore
import bs4  # type: ignore
from bs4 import BeautifulSoup, NavigableString
from PyQt5.QtWidgets import QInputDialog  # type: ignore

sys.path.append(os.path.dirname(__file__))
import pygments  # type: ignore
import pygments.lexers  # type: ignore

from .ankieditorextra import transform_selection
from .assets import AnkiAssetManager, list_plugin_media_files, has_newer_version, sync_assets
from .bs4extra import encode_soup
from .highlighter import format_code_hljs, DISPLAY_STYLE, format_code_pygments
from .hljs import get_available_languages

import anki  # type: ignore

addon_path = os.path.dirname(__file__)
config = aqt.mw and aqt.mw.addonManager.getConfig(__name__)
ASSET_PREFIX = '_ch-'
CSS_ASSETS = [
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


def index_or(l, item, default):
    try:
        return l.index(item)
    except ValueError:
        return default


def ask_for_language(
    parent=None,
    languages_with_current: Optional[Tuple[List[str], Optional[str]]] = None
) -> Optional[str]:
    """
    Shows a dialog asking for a programming language.

    :param parent
    :param languages_with_current Optional[Tuple[List[str], Optional[str]]]:
        The list of options to choose from together with a default selection.
    :rtype Optional[str]: The chosen language if any.
    """
    parent = parent or (aqt.mw and aqt.mw.app.activeWindow()) or aqt.mw
    enter_lang = 'Enter a language'
    provide_lang_long = 'Provide the snippet\'s language (e.g., cpp)'

    if languages_with_current:
        languages, current = languages_with_current
        lang_index_or = partial(index_or, languages)

        default_index = (lang_index_or(current, None)
                         or lang_index_or('cpp', None)
                         or lang_index_or('C++', 0))
        lang, ok = QInputDialog.getItem(parent, enter_lang, provide_lang_long,
                                        languages, default_index)
    else:
        lang, ok = QInputDialog.getText(parent, enter_lang, provide_lang_long)
    return ok and lang


CACHED_SELECTED_LANGUAGES: Dict[str, Optional[str]] = {
    'pygments': None,
    'highlight.js': None,
}


def highlight_action(editor: aqt.editor.Editor) -> None:
    note: Optional[anki.notes.Note] = editor.note
    currentFieldNo = editor.currentField
    global CACHED_SELECTED_LANGUAGES
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

    @enum.unique
    class HIGHLIGHT_METHOD(Enum):
        HLJS = 'highlight.js'
        PYGMENTS = 'pygments'

    @dataclass(frozen=True)
    class HljsConfig:
        language: str

    @dataclass(frozen=True)
    class PygmentsConfig:
        display_style: DISPLAY_STYLE
        language: str

    FormatConfig = Union[HljsConfig, PygmentsConfig]

    def show_dialogs() -> Optional[FormatConfig]:
        parent = (aqt.mw and aqt.mw.app.activeWindow()) or aqt.mw
        highlighter = get_config("default-highlighter", "")
        if not highlighter:
            highlighter, ok = QInputDialog.getItem(
                parent, 'Highlighter', 'Select a highlighter',
                [HIGHLIGHT_METHOD.HLJS.value, HIGHLIGHT_METHOD.PYGMENTS.value])
            if not ok or not highlighter:
                return None

        if highlighter == HIGHLIGHT_METHOD.HLJS.value:
            available_languages = get_available_languages(
                sorted(
                    list_plugin_media_files(editor.mw.col.media,
                                            ASSET_PREFIX)))
            languages_with_current = (available_languages,
                                      CACHED_SELECTED_LANGUAGES[highlighter]
                                      ) if available_languages else None
            language = ask_for_language(
                parent=None, languages_with_current=languages_with_current)
            if language:
                CACHED_SELECTED_LANGUAGES[highlighter] = language
                return HljsConfig(language)
        elif highlighter == HIGHLIGHT_METHOD.PYGMENTS.value:
            display_style, ok = QInputDialog.getItem(parent, 'Display style',
                                                     'Select a display style',
                                                     ['block', 'inline'])
            if not ok:
                return None
            display_style = (DISPLAY_STYLE.BLOCK if display_style == 'block'
                             else DISPLAY_STYLE.INLINE)

            # Filter out lexers with spaces in their name, because
            # get_lexer_by_name can't find them. Lexers with spaces are niche
            # anyway.
            available_languages = [
                t[0] for t in pygments.lexers.get_all_lexers()
                if ' ' not in t[0]
            ]
            languages_with_current = (available_languages,
                                      CACHED_SELECTED_LANGUAGES[highlighter]
                                      ) if available_languages else None
            language = ask_for_language(
                parent=None, languages_with_current=languages_with_current)
            if language:
                CACHED_SELECTED_LANGUAGES[highlighter] = language
                return PygmentsConfig(display_style, language)
        return None

    def format(args: FormatConfig, code) -> Union[bs4.Tag, bs4.BeautifulSoup]:
        if isinstance(args, HljsConfig):
            return format_code_hljs(args.language, code)
        else:
            return format_code_pygments(args.language, args.display_style,
                                        code)

    transform_selection(editor, note, currentFieldNo, show_dialogs,
                        format)  # type: ignore


def on_editor_shortcuts_init(shortcuts: List[Tuple],
                             editor: aqt.editor.Editor) -> None:
    shortcut = get_config("shortcut", "ctrl+'")
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

    def refresh() -> None:
        # Create AnkiAssetManager inside actions and not in setup_menu,
        # because:
        # 1. setup_menu runs in main_window_did_init, which may happen before
        #    profile load
        #    (https://github.com/gregorias/anki-code-highlighter/issues/22).
        # 2. create_anki_asset_manager requires a profile to be loaded.
        anki_asset_manager = create_anki_asset_manager(main_window.col)
        anki_asset_manager.delete_assets()
        anki_asset_manager.install_assets()

    def delete() -> None:
        anki_asset_manager = create_anki_asset_manager(main_window.col)
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
