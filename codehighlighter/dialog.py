"""Functions for working with dialogs.

This module contains functions for working with dialogs and wizards. This
module contains code that touches both the Anki GUI and depends on
highlighters. The highlighting functionality must not depend on this module.
"""
from typing import List, Optional
from aqt.qt import QInputDialog

__all__ = ["showChoiceDialog"]


def showChoiceDialog(parent, title: str, message: str, options: List[str],
                     current: Optional[int]) -> Optional[str]:
    """
    Shows a choice selection dialog.

    :param parent: A parent widget.
    :param title str
    :param message str
    :param options List[str]: A list of available options.
    :param current Optional[int]: The option's index to preselect.
    :rtype Optional[str]: Selected option if any.
    :raises Exception
    """
    if current and not (current >= 0 and current < len(options)):
        raise Exception(f"The provided default index, {current}, " +
                        f"is not within option range. " +
                        f"The option range size is {len(options)}.")
    if current is None:
        label, ok = QInputDialog.getItem(parent, title, message, options)
    else:
        # If current is None, QInputDialog.getItem will throw a type error at
        # runtime.
        label, ok = QInputDialog.getItem(parent, title, message, options,
                                         current)
    return (ok and label) or None
