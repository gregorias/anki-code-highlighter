from functools import partial
import random
import re
import typing
from typing import Callable, Optional, Union

import anki
from aqt.utils import showWarning  # type: ignore
import aqt  # type: ignore
import bs4  # type: ignore
from bs4 import BeautifulSoup, NavigableString

from .bs4extra import create_soup, encode_soup, replace_br_tags_with_newlines

__all__ = [
    'extract_field_from_web_editor',
    'extract_selection_from_field',
    'transform_selection',
]


# A helper function for `transform_selection` exposed for testing.
def transform_elements_with_id(html: str, id: str,
                               replace: Callable[[str],
                                                 Union[bs4.Tag,
                                                       bs4.BeautifulSoup]]):
    soup = create_soup(html)
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


def extract_selection_from_field(field_html: str, id: str) -> Optional[str]:
    """
    Returns HTML of a selected text.

    :param field_html str: The HTML of the note field.
    :param id str: The ID of the selection.
    :rtype Optional[str]: On a failure to find the selection, returns None.
    """
    soup = create_soup(field_html)
    for element in soup.find_all(id=id):
        return element.decode_contents()
    return None


def eval_js_with_callback(webview: aqt.editor.EditorWebView, js: str,
                          callback: Callable[[typing.Any], None]) -> None:
    """
    Evaluates JavaScript in the webview and calls `callback` with the result.

    Wraps the code inside a try-catch statement. On exception, gives the
    callback a dictionary ({'error': {'name': str, 'message', str}}) or just
    {'error': str}.

    :param webview:
    :param js:
    :param callback:
    :return: None
    """
    webview.evalWithCallback(
        f"""
        (function() {{
           try {{
               {js}
           }} catch(e) {{
               if ('name' in e && 'message' in e)
                   return {{ error: {{ name: e.name, message: e.message }} }}
               return {{ error: JSON.stringify(e) }}
           }}
        }})();""", callback)


def extract_my_span_from_web_editor(web_editor_html: str,
                                    span_id: str) -> Optional[str]:
    """Returns the HTML of the spanned selection."""
    soup = create_soup(web_editor_html)
    for element in soup.find_all(id=span_id):
        return element.decode_contents()
    return None


# This function returns `str` and not bs4.Tag, because this function will be
# unit-tested, and I want unit-tests to also test the encoding functionality.
def highlight_selection(
        selection: str,
        highlighter: Callable[[str], Optional[bs4.Tag]]) -> Optional[str]:
    """
    Highlights a selection from a field.

    This function sanitizes the input by removing HTML markup. It returns an
    encoded HTML.

    :param selection: An HTML string representing the code.
    :param highlighter: A function that highlights the code.
    :return: The highlighter HTML tag.
    """
    selection = replace_br_tags_with_newlines(selection)
    selection_soup = create_soup(selection)
    highlighted_selection = highlighter(selection_soup.text)
    return encode_soup(
        highlighted_selection) if highlighted_selection else None


# This function has used `editor.web.eval` previously, but that executed
# asynchronously, so there was no guarantee that editor.note would be up to
# date with changes made by the JavaScript.
# I arrived at the .evalWithCallback approach thanks to:
# https://forums.ankiweb.net/t/how-do-i-synchronously-sync-changes-in-ankiwebview-to-the-data-model-in-python/22920
def transform_selection(editor: aqt.editor.Editor, note: anki.notes.Note,
                        currentField: int,
                        highlight: Callable[[str], Optional[bs4.Tag]],
                        onError: Callable[[str], typing.Any]) -> None:
    """
    Transforms selected text using `transform`.

    :param editor aqt.editor.Editor
    :param note anki.notes.Note: The note under edition. Usually `editor.note`.
    :param currentField int The ID of the field under focus.
    :param highlight Callable[[str], bs4.Tag]:
        The highlighting function that receives code snippets and returns HTML
        with highlighting information.
    :param onError Callable[[str], typing.Any]:
        The callback function that is called if an unrecoverable error has
        occurred. Provides an error message.
    :rtype None
    """
    random_id = str(random.randint(0, 10000))
    highlight_html2html: Callable[[str], Optional[str]] = partial(
        highlight_selection, highlighter=highlight)
    failed_to_find_selection = 'Failed to find a selection.'

    def transform_field(selection_return: typing.Any) -> None:

        def safe_get(d, key):
            if isinstance(d, dict):
                return d.get(key)
            return None

        if not safe_get(selection_return, 'field'):
            error = safe_get(selection_return, 'error')
            message = safe_get(error, 'message')
            if message == failed_to_find_selection:
                onError("Failed to find a code selection to highlight." +
                        " You need to select a code snippet " +
                        "before triggerring the highlight action.")
            elif message == (
                    "Failed to execute 'surroundContents' on 'Range': " +
                    "The Range has partially selected a non-Text node."):
                # Make sure this error message is clear
                # (https://github.com/gregorias/anki-code-highlighter/issues/60)
                onError(
                    "The selection splits an HTML node, which prevents the " +
                    "highlighting plugin from proceeding.\n" +
                    "Make sure that you select entire HTML elements, e.g., " +
                    "if your code is `<span>hello</span>world`, don't select" +
                    " just `ello</span>world`.\n" +
                    "You can refactor your code snippet in the HTML editor " +
                    "(https://docs.ankiweb.net/editing.html#editing-features)"
                    + " before highlighting.")
            else:
                onError(
                    f"An unknown transformation error has occurred " +
                    f"(repr(selection_return)). " +
                    " Report it to the developer at " +
                    "https://github.com/gregorias/anki-code-highlighter/issues/new."
                )
            return None

        field = extract_field_from_web_editor(selection_return['field'])
        if field is None:
            onError(
                f"Failed to extract the field from the web editor. " +
                f"({repr(selection_return)}). " +
                "Report it to the developer at " +
                "https://github.com/gregorias/anki-code-highlighter/issues/new."
            )
            return None

        selection = extract_selection_from_field(field, random_id)
        if selection is None:
            onError(
                f"Failed to extract the selection from the field. " +
                f"({repr(selection_return)}, {repr(random_id)}). " +
                "Report it to the developer at " +
                "https://github.com/gregorias/anki-code-highlighter/issues/new."
            )
            return None

        # On failure, revert back to selection, so that we don't delete user
        # input during replacement.
        highlighted_selection = highlight_html2html(selection) or selection

        # Replace the selection span directly in the webview.
        #
        # This approach is simpler and more robust than replacing the selection
        # inside Python and flushing the new note to Anki's DB:
        # * We avoid having to figure out flush field changes DB and see them
        #   reflected in the webview.
        # * The field's representation in webview and the serialized note can
        #   differ significantly. Mathjax expressions in a webview are a
        #   complex HTML element, while they get serialized to `\(expr\)`
        #   inside a note. Not having to reconcile that is good, as we don't
        #   have to touch non-selection code.
        eval_js_with_callback(
            editor.web, f"""
            let selection = document.activeElement.shadowRoot.getElementById({random_id});
            // A hack against spurious br-tags that get inserted by the Anki editor.
            // https://github.com/gregorias/anki-code-highlighter/issues/51
            if (selection.nextElementSibling?.tagName === "BR" && selection.nextElementSibling.nextSibling === null) {{
                selection.nextElementSibling.remove();
            }}
            selection.outerHTML = {repr(highlighted_selection)};
            return null;""", lambda _: None)

    # Not using Anki's own `wrap` function uses `document.execCommand`, which
    # is deprecated and doesn't work for inline selections.
    # Using the Range API is better as it doesn't suffer from those drawbacks.
    #
    # We need to wrap the selection in a tag, because `transform` may lose
    # focus (e.g., by presenting a modal dialog) and with it, the selection.
    eval_js_with_callback(
        editor.web, f"""
        let selection = document.activeElement.shadowRoot.getSelection();
        if (selection.rangeCount == 0)
           return {{ error: {{ name: 'InvalidStateError',
                               message: '{failed_to_find_selection}' }} }};
        const range = selection.getRangeAt(selection.rangeCount - 1);
        if (!range) return;
        const spanTag = document.createElement('span')
        spanTag['id'] = '{random_id}'
        range.surroundContents(spanTag);
        return {{ field: document.activeElement.shadowRoot.innerHTML }};
        """, transform_field)
