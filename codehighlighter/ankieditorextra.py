from functools import partial
import random
import typing
from typing import Callable, Union

import anki
import aqt  # type: ignore
import bs4  # type: ignore
from bs4 import BeautifulSoup, NavigableString

from .bs4extra import encode_soup

__all__ = ['transform_selection']


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


# get_transform_config is necessary, because it may show a modal dialog, which
# would cause the result of editor.web.eval to be committed to the database,
# updating editor.note.
# I couldn't make this function to work with editor.web.evalWithCallback, the
# note didn't get updated in the continuation.
# https://forums.ankiweb.net/t/how-do-i-synchronously-sync-changes-in-ankiwebview-to-the-data-model-in-python/22920
def transform_selection(
        editor: aqt.editor.Editor, note: anki.notes.Note, currentField: int,
        get_transform_config: Callable[[], T],
        transform: Callable[[T, str], Union[bs4.Tag,
                                            bs4.BeautifulSoup]]) -> None:
    """
    Transforms selected text using `transform`.

    :param editor aqt.editor.Editor
    :param note anki.notes.Note: The note under edition. Usually `editor.note`.
    :param currentField int The ID of the field under focus.
    :param get_transform_config Callable[[], T]:
        A function that returns a configuration for the transformation, e.g.,
        by showing dialogs asking for user input.
    :param transform Callable[[T, str], Union[bs4.Tag, bs4.BeautifulSoup]]:
        The transform function that receives selected text and returns
        transformed tag or soup.
    :rtype None
    """
    random_id = str(random.randint(0, 10000))
    # Not using Anki's own `wrap` function uses `document.execCommand`, which
    # is deprecated and doesn't work for inline selections.
    # Using the Range API is better as it doesn't suffer from those drawbacks.
    #
    # We need to wrap the selection in a tag, because `transform` may lose
    # focus (e.g., by presenting a modal dialog) and therefore the selection.
    editor.web.eval(f"""
      (function() {{
         let selection = document.activeElement.shadowRoot.getSelection();
         if (selection.rangeCount == 0) return;
         const range = selection.getRangeAt(selection.rangeCount - 1);
         if (!range) return;
         const spanTag = document.createElement('span')
         spanTag['id'] = '{random_id}'
         range.surroundContents(spanTag);
      }})();""")
    transformData = get_transform_config()
    note.fields[currentField] = transform_elements_with_id(
        note.fields[currentField], random_id, partial(transform,
                                                      transformData))

    # That's how aqt.editor.onHtmlEdit saves cards.
    # It's better than `editor.mw.reset()`, because the latter loses focus.
    # Calls like editor.mw.reset() or editor.loadNote() are necessary to save
    # HTML changes.
    if not editor.addMode:
        note.flush()  # type: ignore
    editor.loadNoteKeepingFocus()
