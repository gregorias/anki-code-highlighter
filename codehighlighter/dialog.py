"""Functions for working with dialogs.

This module contains functions for working with dialogs and wizards. This
module contains code that touches both the Anki GUI and depends on
highlighters. The highlighting functionality must not depend on this module.
"""
from dataclasses import dataclass
import enum
from enum import Enum
from typing import List, Optional, Union

from aqt.qt import QInputDialog

from .listextra import index_or
from . import hljs
from . import hljslangs

__all__ = [
    "showChoiceDialog",
    "HIGHLIGHT_METHOD",
    "highlight_method_name_to_enum",
    "HljsConfig",
    "ask_for_highlight_method",
    "ask_for_language",
]


def showChoiceDialog(parent, title: str, message: str, options: List[str],
                     current: Union[str, int, None]) -> Optional[str]:
    """
    Shows a choice selection dialog.

    :param parent: A parent widget.
    :param title str
    :param message str
    :param options List[str]: A list of available options.
    :param current Optional[int]: The option or its index to preselect.
    :rtype Optional[str]: Selected option if any.
    :raises Exception
    """
    if current is None:
        label, ok = QInputDialog.getItem(parent, title, message, options)
    else:
        # Turn current into an index if it’s a string.
        if isinstance(current, str):
            current_idx = index_or(options, current, None)
            if current_idx is None:
                raise Exception(f"The provided default option, {current}, " +
                                "is not within the provided options.")
        else:
            current_idx = current
            if not (current >= 0 and current < len(options)):
                raise Exception(f"The provided default index, {current}, " +
                                "is not within the option range. " +
                                f"The option range size is {len(options)}.")

        # If current_idx is None, QInputDialog.getItem will throw a type error
        # at runtime.
        label, ok = QInputDialog.getItem(parent, title, message, options,
                                         current_idx)
    return (ok and label) or None


@enum.unique
class HIGHLIGHT_METHOD(Enum):
    HLJS = 'highlight.js'
    PYGMENTS = 'pygments'


def highlight_method_name_to_enum(name: str) -> Optional[HIGHLIGHT_METHOD]:
    for m in list(HIGHLIGHT_METHOD):
        if m.value == name:
            return m
    return None


def ask_for_highlight_method(
        parent,
        current: Optional[HIGHLIGHT_METHOD]) -> Optional[HIGHLIGHT_METHOD]:
    """
    Shows a dialog asking for a highlighting method.
    """
    method_value = showChoiceDialog(
        parent,
        'Highlighter',
        'Select a highlighter',
        options=[m.value for m in list(HIGHLIGHT_METHOD)],
        current=None if current is None else current.value)
    if method_value is None:
        return None
    return highlight_method_name_to_enum(method_value)


def ask_for_language(
    parent,
    languages: List[str],
    current: Optional[str],
) -> Optional[str]:
    """
    Shows a dialog asking for a programming language.
    """
    enter_lang = 'Language'
    provide_lang_long = 'Select the snippet’s language (e.g., C++)'

    if current not in languages:
        current = None

    return showChoiceDialog(parent, enter_lang, provide_lang_long, languages,
                            current)


@dataclass(frozen=True)
class HljsConfig:
    language: Optional[hljslangs.Language]


def ask_for_hljs_config(parent, current: HljsConfig) -> Optional[HljsConfig]:
    """
    Shows a wizard that configures hljs.

    :param parent
    :param current HljsConfig: The default configuration.
    :return Optional[HljsConfig]:
    """
    language_dict = hljs.get_available_languages_as_dict()
    language_names = list(sorted(language_dict.keys()))
    language_name = ask_for_language(parent=None,
                                     languages=language_names,
                                     current=current.language
                                     and current.language.name)
    if not language_name:
        return None
    return HljsConfig(language_dict.get(language_name, None))
