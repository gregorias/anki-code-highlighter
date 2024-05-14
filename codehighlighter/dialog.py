"""Functions for working with dialogs.

This module contains functions for working with dialogs and wizards. This
module contains code that touches both the Anki GUI and depends on
highlighters. The highlighting functionality must not depend on this module.
"""
from typing import List, Optional, Union
from aqt.qt import QInputDialog

from .listextra import index_or

__all__ = ["showChoiceDialog"]


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
