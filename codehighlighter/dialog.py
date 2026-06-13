"""Functions for working with dialogs and wizards.

This module contains functions for working with dialogs and wizards.

This module contains code that touches both the Anki GUI and depends on
highlighters.
The highlighting functionality must not depend on this module. Also, for
minimizing responsibility, serialization of state should also be outside of
this module.
"""

import dataclasses
import enum
import typing
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Union

from aqt.qt import QInputDialog

from . import pygments_highlighter
from .fuzzy_finder_dialog import FuzzyFinderDialog
from .listextra import index_or
from .serialization import JSONObjectConverter

__all__ = [
    "showChoiceDialog",
    "DISPLAY_STYLE",
    "ask_for_display_style",
    "ask_for_language",
]


def showChoiceDialog(
    parent, title: str, message: str, options: List[str], current: Union[str, int, None]
) -> Optional[str]:
    """Shows a choice selection dialog.

    Args:
        parent: A parent widget.
        title: The dialog title.
        message: The message to display.
        options: A list of available options.
        current: The option or its index to preselect.

    Returns:
        Selected option if any.

    Raises:
        Exception: If the default option or index is invalid or out of range.
    """
    if current is None:
        label, ok = QInputDialog.getItem(parent, title, message, options)
    else:
        # Turn current into an index if it’s a string.
        if isinstance(current, str):
            current_idx = index_or(options, current, None)
            if current_idx is None:
                raise Exception(
                    f"The provided default option, {current}, "
                    + "is not within the provided options."
                )
        else:
            current_idx = current
            if not (current >= 0 and current < len(options)):
                raise Exception(
                    f"The provided default index, {current}, "
                    + "is not within the option range. "
                    + f"The option range size is {len(options)}."
                )

        # If current_idx is None, QInputDialog.getItem will throw a type error
        # at runtime.
        label, ok = QInputDialog.getItem(parent, title, message, options, current_idx)
    return (ok and label) or None


def ask_for_language(
    parent,
    languages: List[str],
    current: Optional[str],
) -> Optional[str]:
    """Shows a dialog asking for a programming language with a fuzzy finder.

    Args:
        parent: The parent widget.
        languages: A list of available programming languages.
        current: The default language to preselect.

    Returns:
        The selected language, or None if cancelled.
    """
    enter_lang = "Language"
    provide_lang_long = "Select the snippet’s language (e.g., C++)"

    if current not in languages:
        current = None

    return FuzzyFinderDialog.ask(
        parent, enter_lang, provide_lang_long, languages, current
    )


@enum.unique
class DISPLAY_STYLE(Enum):
    BLOCK = 1
    INLINE = 2


class DisplayStyleJSONConverter(JSONObjectConverter[DISPLAY_STYLE]):

    def deconvert(self, json_object) -> Optional[DISPLAY_STYLE]:
        if json_object == 1:
            return DISPLAY_STYLE.BLOCK
        elif json_object == 2:
            return DISPLAY_STYLE.INLINE
        else:
            return None

    def convert(self, t: DISPLAY_STYLE):
        return t.value


def ask_for_display_style(parent, current: DISPLAY_STYLE) -> Optional[DISPLAY_STYLE]:
    """Shows a dialog asking for a display style.

    Args:
        parent: The parent widget.
        current: The default display style.

    Returns:
        The selected display style, or None if cancelled.
    """
    display_style = showChoiceDialog(
        parent,
        "Display style",
        "Select a display style",
        ["block", "inline"],
        current="block" if current == DISPLAY_STYLE.BLOCK else "inline",
    )
    if display_style == "block":
        return DISPLAY_STYLE.BLOCK
    elif display_style == "inline":
        return DISPLAY_STYLE.INLINE
    else:
        return None


@dataclass(frozen=True)
class PygmentsConfig:
    display_style: DISPLAY_STYLE
    language: str


class PygmentsConfigJSONConverter(JSONObjectConverter[PygmentsConfig]):

    def __init__(self):
        self.display_style_converter = DisplayStyleJSONConverter()

    def deconvert(self, json_object: typing.Any) -> Optional[PygmentsConfig]:
        display_style = self.display_style_converter.deconvert(
            json_object["display_style"]
        )

        if display_style is None:
            return None

        return PygmentsConfig(display_style, json_object["language"])

    def convert(self, t: PygmentsConfig):
        config_dict = dataclasses.asdict(t)
        config_dict["display_style"] = self.display_style_converter.convert(
            config_dict["display_style"]
        )
        return config_dict


def ask_for_pygments_config(
    parent, current: PygmentsConfig
) -> Optional[PygmentsConfig]:
    """Shows a wizard that configures Pygments.

    Args:
        parent: The parent widget.
        current: The default configuration.

    Returns:
        The selected Pygments configuration, or None if cancelled.
    """
    display_style = ask_for_display_style(parent, current.display_style)
    if display_style is None:
        return None

    available_languages = list(pygments_highlighter.get_available_languages())
    language = ask_for_language(
        parent=parent, languages=available_languages, current=current.language
    )
    if not language:
        return None

    return PygmentsConfig(display_style, language)


@dataclass
class HighlighterWizardState:
    """The state of the highlighter wizard.

    It provides useful defaults to preselect.

    Attributes:
        pygments_config: The Pygments configuration.
    """

    pygments_config: PygmentsConfig = PygmentsConfig(
        display_style=DISPLAY_STYLE.BLOCK, language="C++"
    )


class HighlighterWizardStateJSONConverter(JSONObjectConverter[HighlighterWizardState]):

    def __init__(self):
        self.pc = PygmentsConfigJSONConverter()

    def deconvert(self, json_object) -> Optional[HighlighterWizardState]:
        pc = self.pc.deconvert(json_object["pygments_config"])
        if pc is None:
            return None

        return HighlighterWizardState(pc)

    def convert(self, t: HighlighterWizardState):
        config_dict = dict()
        config_dict["pygments_config"] = self.pc.convert(t.pygments_config)
        return config_dict


# The highlighter config chosen by the user.
HighlighterConfig = PygmentsConfig


def ask_for_highlighter_config(
    parent,
    state: HighlighterWizardState,
) -> Tuple[Optional[HighlighterConfig], HighlighterWizardState]:
    """Shows a wizard that configures a highlighter.

    This wizard comes with a state. Users like to have sticky options.

    Args:
        parent: The parent widget.
        state: The state of the wizard to use.

    Returns:
        A tuple containing the selected configuration (or None if cancelled)
        and the updated wizard state.
    """
    pygments_config = ask_for_pygments_config(parent, state.pygments_config)
    if pygments_config is not None:
        return (
            pygments_config,
            dataclasses.replace(state, pygments_config=pygments_config),
        )

    return (None, state)
