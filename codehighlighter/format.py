"""Functionalities related to generic formatting and highlighting."""
from typing import Callable, Protocol, TypeVar

from .html import PlainString


class Clipboard(Protocol):

    def text(self) -> str:
        pass


class EmptyClipboard(Clipboard):
    """A clipboard that is always empty."""

    def text(self) -> str:
        return ""


HighlightedCode = TypeVar('HighlightedCode')


def format_selected_code(code: PlainString,
                         highlight: Callable[[PlainString], HighlightedCode],
                         clipboard: Clipboard) -> HighlightedCode:
    """Formats a code block selected by the user.

    If no code is selected, the clipboard is used instead.

    :param code: User-selected code string in plaintext to be formatted.
    :param highlight: The function that does the highlighting
    :param clipboard: A clipboard.
    :return: A formatted code block.
    """
    if len(code) == 0:
        code = PlainString(clipboard.text())
    return highlight(code)
