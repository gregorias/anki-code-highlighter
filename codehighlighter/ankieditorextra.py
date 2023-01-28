from functools import partial
import random
import re
import typing
from typing import Callable, Optional, Union

import anki
import aqt  # type: ignore
import bs4  # type: ignore
from bs4 import BeautifulSoup, NavigableString

from .bs4extra import encode_soup

__all__ = ['extract_field_from_web_editor', 'transform_selection']


# A helper function for `transform_selection` exposed for testing.
def transform_elements_with_id(html: str, id: str,
                               replace: Callable[[str],
                                                 Union[bs4.Tag,
                                                       bs4.BeautifulSoup]]):
    soup = BeautifulSoup(html, features='html.parser')
    for element in soup.find_all(id=id):
        element.replace_with(replace(element.decode_contents()))
    return encode_soup(soup)


T = typing.TypeVar('T')


def extract_field_from_web_editor(web_editor_html: str) -> Optional[str]:
    """
    Returns HTML of a note field.

    :param web_editor_html str: The innerHTML of the webview's shadow root
      containing the editing widget.
    :rtype Optional[str]: On a failure to find the field, returns None.
    """
    result = re.search('<anki-editable[^>]*>(.*)</anki-editable>',
                       web_editor_html, re.MULTILINE | re.DOTALL)
    if result is None:
        return None
    return result.group(1)


# This function has used `editor.web.eval` previously, but that executed
# asynchronously, so there was no guarantee that editor.note would be up to
# date with changes made by the JavaScript.
# I arrived at the .evalWithCallback approach thanks to:
# https://forums.ankiweb.net/t/how-do-i-synchronously-sync-changes-in-ankiwebview-to-the-data-model-in-python/22920
def transform_selection(
    editor: aqt.editor.Editor, note: anki.notes.Note, currentField: int,
    transform: Callable[[str], Union[bs4.Tag, bs4.BeautifulSoup,
                                     None]]) -> None:
    """
    Transforms selected text using `transform`.

    :param editor aqt.editor.Editor
    :param note anki.notes.Note: The note under edition. Usually `editor.note`.
    :param currentField int The ID of the field under focus.
    :param transform Callable[[str], Union[bs4.Tag, bs4.BeautifulSoup, None]]:
        The transform function that receives selected text and returns
        transformed tag, or None on error.
    :rtype None
    """
    random_id = str(random.randint(0, 10000))

    def transform_field(web_editor_html: str) -> None:
        field = extract_field_from_web_editor(web_editor_html)

        def format(code: str) -> Union[bs4.Tag, bs4.BeautifulSoup]:
            # If the provided transform has failed, use an effect-less
            # transform to clean up annotations.
            return transform(code) or bs4.BeautifulSoup(code,
                                                        features='html.parser')

        if field is None:
            # Use note.fields[currentField] as a backup.
            field = note.fields[currentField]

        note.fields[currentField] = transform_elements_with_id(
            field, random_id, format)

        # That's how aqt.editor.onHtmlEdit saves cards.
        # It's better than `editor.mw.reset()`, because the latter loses focus.
        # Calls like editor.mw.reset() or editor.loadNote() are necessary to save
        # HTML changes.
        if not editor.addMode:
            note.flush()  # type: ignore
        editor.loadNoteKeepingFocus()

    # Not using Anki's own `wrap` function uses `document.execCommand`, which
    # is deprecated and doesn't work for inline selections.
    # Using the Range API is better as it doesn't suffer from those drawbacks.
    #
    # We need to wrap the selection in a tag, because `transform` may lose
    # focus (e.g., by presenting a modal dialog) and with it, the selection.
    editor.web.evalWithCallback(
        f"""
      (function() {{
         let selection = document.activeElement.shadowRoot.getSelection();
         if (selection.rangeCount == 0) return;
         const range = selection.getRangeAt(selection.rangeCount - 1);
         if (!range) return;
         const spanTag = document.createElement('span')
         spanTag['id'] = '{random_id}'
         range.surroundContents(spanTag);
         return document.activeElement.shadowRoot.innerHTML;
      }})();""", transform_field)
