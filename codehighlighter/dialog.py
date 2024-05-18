"""Functions for working with dialogs and wizards.

This module contains functions for working with dialogs and wizards.

This module contains code that touches both the Anki GUI and depends on
highlighters.
The highlighting functionality must not depend on this module. Also, for
minimizing responsibility, serialization of state should also be outside of
this module.
"""
import dataclasses
from dataclasses import dataclass
import enum
from enum import Enum
from typing import Callable, List, Optional, Tuple, Union

from aqt.qt import QInputDialog

from .listextra import index_or
from .serialization import JSONObjectConverter
from . import hljs
from . import hljslangs
from . import pygments_highlighter

__all__ = [
    "showChoiceDialog",
    "HIGHLIGHT_METHOD",
    "highlight_method_name_to_enum",
    "DISPLAY_STYLE",
    "HljsConfig",
    "ask_for_highlight_method",
    "ask_for_display_style",
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


class HighlightMethodJSONConverter(JSONObjectConverter[HIGHLIGHT_METHOD]):

    def deconvert(self, json_object) -> Optional[HIGHLIGHT_METHOD]:
        return highlight_method_name_to_enum(json_object)

    def convert(self, t: HIGHLIGHT_METHOD):
        return t.value


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


def ask_for_display_style(parent,
                          current: DISPLAY_STYLE) -> Optional[DISPLAY_STYLE]:
    """
    Shows a dialog asking for a display style.
    """
    display_style = showChoiceDialog(
        parent,
        'Display style',
        'Select a display style', ['block', 'inline'],
        current='block' if current == DISPLAY_STYLE.BLOCK else 'inline')
    if display_style == 'block':
        return DISPLAY_STYLE.BLOCK
    elif display_style == 'inline':
        return DISPLAY_STYLE.INLINE
    else:
        return None


@dataclass(frozen=True)
class HljsConfig:
    language: Optional[hljslangs.Language]


class HljsConfigJSONConverter(JSONObjectConverter[HljsConfig]):

    def deconvert(self, json_object) -> Optional[HljsConfig]:
        if json_object is None:
            return HljsConfig(None)

        for lang in hljslangs.languages:
            if lang.alias == json_object:
                return HljsConfig(lang)
        return None

    def convert(self, t: HljsConfig):
        return t.language and t.language.alias


def ask_for_hljs_config(parent, current: HljsConfig) -> Optional[HljsConfig]:
    """
    Shows a wizard that configures hljs.

    :param parent
    :param current HljsConfig: The default configuration.
    :return Optional[HljsConfig]
    """
    language_dict = hljs.get_available_languages_as_dict()
    language_names = list(sorted(language_dict.keys()))
    language_name = ask_for_language(parent=parent,
                                     languages=language_names,
                                     current=current.language
                                     and current.language.name)
    if not language_name:
        return None
    return HljsConfig(language_dict.get(language_name, None))


@dataclass(frozen=True)
class PygmentsConfig:
    display_style: DISPLAY_STYLE
    language: str


class PygmentsConfigJSONConverter(JSONObjectConverter[PygmentsConfig]):

    def __init__(self):
        self.display_style_converter = DisplayStyleJSONConverter()

    def deconvert(self, json_object) -> Optional[PygmentsConfig]:
        return PygmentsConfig(
            self.display_style_converter.deconvert(
                json_object['display_style']),
            json_object['language'],
        )

    def convert(self, t: PygmentsConfig):
        config_dict = dataclasses.asdict(t)
        config_dict['display_style'] = self.display_style_converter.convert(
            config_dict['display_style'])
        return config_dict


def ask_for_pygments_config(
        parent, current: PygmentsConfig) -> Optional[PygmentsConfig]:
    """
    Shows a wizard that configures hljs.

    :param parent
    :param current PygmentsConfig: The default configuration.
    :return Optional[PygmentsConfig]
    """
    display_style = ask_for_display_style(parent, current.display_style)
    if display_style is None:
        return None

    available_languages = list(
        sorted(pygments_highlighter.get_available_languages()))
    language = ask_for_language(parent=parent,
                                languages=available_languages,
                                current=current.language)
    if not language:
        return None

    return PygmentsConfig(display_style, language)


@dataclass
class HighlighterWizardState:
    """
    The state of the highlighter wizard.

    It provides useful defaults to preselect.
    """
    highlighter: HIGHLIGHT_METHOD = HIGHLIGHT_METHOD.HLJS
    hljs_config: HljsConfig = HljsConfig(
        hljs.get_available_languages_as_dict().get("C++", None))
    pygments_config: PygmentsConfig = PygmentsConfig(
        display_style=DISPLAY_STYLE.BLOCK, language="C++")


class HighlighterWizardStateJSONConverter(
        JSONObjectConverter[HighlighterWizardState]):

    def __init__(self):
        self.hm = HighlightMethodJSONConverter()
        self.hc = HljsConfigJSONConverter()
        self.pc = PygmentsConfigJSONConverter()

    def deconvert(self, json_object) -> Optional[HighlighterWizardState]:
        return HighlighterWizardState(
            self.hm.deconvert(json_object['highlighter']),
            self.hc.deconvert(json_object['hljs_config']),
            self.pc.deconvert(json_object['pygments_config']))

    def convert(self, t: HighlighterWizardState):
        config_dict = dict()
        config_dict['highlighter'] = self.hm.convert(t.highlighter)
        config_dict['hljs_config'] = self.hc.convert(t.hljs_config)
        config_dict['pygments_config'] = self.pc.convert(t.pygments_config)
        return config_dict


# The highlighter config chosen by the user.
HighlighterConfig = Union[HljsConfig, PygmentsConfig]


def ask_for_highlighter_config(
    parent, state: HighlighterWizardState,
    get_highlighter: Callable[[HIGHLIGHT_METHOD], Optional[HIGHLIGHT_METHOD]]
) -> Tuple[Optional[HighlighterConfig], HighlighterWizardState]:
    """
    Shows a wizard that configures a highlighter.

    This wizard comes with a state. Users like to have sticky options.

    :param parent
    :param state HighlighterWizardState: The state of the wizard to use.
    :param get_highlighter: A function that fetches the selected highlight method given a preselected default.
    :return: The selected config and a new state.
    """
    highlighter = get_highlighter(state.highlighter)

    if highlighter is None:
        return (None, state)

    state = dataclasses.replace(state, highlighter=highlighter)

    if highlighter == HIGHLIGHT_METHOD.HLJS:
        hljs_config = ask_for_hljs_config(parent, state.hljs_config)
        if hljs_config is not None:
            return (hljs_config,
                    dataclasses.replace(state, hljs_config=hljs_config))
    elif highlighter == HIGHLIGHT_METHOD.PYGMENTS:
        pygments_config = ask_for_pygments_config(parent,
                                                  state.pygments_config)
        if pygments_config is not None:
            return (pygments_config,
                    dataclasses.replace(state,
                                        pygments_config=pygments_config))

    return (None, state)
