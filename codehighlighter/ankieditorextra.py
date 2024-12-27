import random
import typing
from typing import Callable, Optional

import anki
import aqt  # type: ignore
import bs4  # type: ignore

from .bs4extra import encode_soup
from .html import HtmlString, PlainString

__all__ = [
    'transform_selection',
]

T = typing.TypeVar('T')


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


def wrap_and_get_selection(webview: aqt.editor.EditorWebView, wrap_id: str,
                           cb):
    """
    Wraps a field selection in a span tag and returns the selected text.
    """
    failed_to_find_selection = 'Failed to find a selection.'
    # Not using Anki's own `wrap` function uses `document.execCommand`, which
    # is deprecated and doesn't work for inline selections.
    # Using the Range API is better as it doesn't suffer from those drawbacks.
    #
    # We need to wrap the selection in a tag, because `transform` may lose
    # focus (e.g., by presenting a modal dialog) and with it, the selection.
    #
    # We return the rendered selected text. A previous version of this code
    # return the inner HTML (`document.activeElement.shadowRoot.innerHTLM`).
    # The former is more useful: the user usually cares about highlighting the
    # text they see, not some abstract HTML representation. Having the reparse
    # HTML was more complex and fragile.
    eval_js_with_callback(
        webview, f"""
        let selection = document.activeElement.shadowRoot.getSelection();
        const selectionText = selection.toString();
        if (selection.rangeCount == 0)
           return {{ error: {{ name: 'InvalidStateError',
                               message: '{failed_to_find_selection}' }} }};
        const range = selection.getRangeAt(selection.rangeCount - 1);
        if (!range) return;
        const spanTag = document.createElement('span')
        spanTag['id'] = '{wrap_id}'
        try {{
            range.surroundContents(spanTag);
            return {{ selectionText }};
        }} catch (e) {{
            if (!(e instanceof DOMException)) {{
                throw e
            }}
            // Try an alternative approach.
            let selectedContent = range.extractContents();
            spanTag.appendChild(selectedContent);
            range.insertNode(spanTag);
            return {{ selectionText }};
        }}
        """, cb)


# This function returns `str` and not bs4.Tag, because this function will be
# unit-tested, and I want unit-tests to also test the encoding functionality.
def highlight_selection(
    selection: PlainString, highlighter: Callable[[PlainString],
                                                  Optional[bs4.Tag]]
) -> Optional[HtmlString]:
    """
    Highlights a selection from a field.

    It returns an encoded HTML.

    :param selection: A plaintext string representing the code.
    :param highlighter: A function that highlights the code.
    :return: The highlighter HTML tag.
    """
    highlighted_selection = highlighter(selection)
    return encode_soup(
        highlighted_selection) if highlighted_selection else None


# This function has used `editor.web.eval` previously, but that executed
# asynchronously, so there was no guarantee that editor.note would be up to
# date with changes made by the JavaScript.
# I arrived at the .evalWithCallback approach thanks to:
# https://forums.ankiweb.net/t/how-do-i-synchronously-sync-changes-in-ankiwebview-to-the-data-model-in-python/22920
def transform_selection(editor: aqt.editor.Editor, note: anki.notes.Note,
                        currentField: int,
                        highlight: Callable[[PlainString], Optional[bs4.Tag]],
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
    failed_to_find_selection = 'Failed to find a selection.'

    def transform_field(selection_return: typing.Any) -> None:

        def safe_get(d, key):
            if isinstance(d, dict):
                return d.get(key)
            return None

        def finalize_selection_span(action) -> None:
            # Replace the selection span directly in the webview.
            #
            # This approach is simpler and more robust than replacing the selection
            # inside Python and flushing the new note to Anki's DB:
            #
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
                {action}
                return null;""", lambda _: None)

        if safe_get(selection_return, 'selectionText') is None:
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
                    "An unknown transformation error has occurred " +
                    f"({repr(selection_return)}). " +
                    " Report it to the developer at " +
                    "https://github.com/gregorias/anki-code-highlighter/issues/new."
                )
            return None

        selection_text = selection_return['selectionText']
        if selection_text is None:
            onError(
                "Failed to extract the selected text from the web editor. " +
                f"({repr(selection_return)}). " +
                "Report it to the developer at " +
                "github.com/gregorias/anki-code-highlighter/issues/new")
            return None

        highlighted_selection = highlight_selection(selection_text,
                                                    highlighter=highlight)
        if highlighted_selection:
            finalize_selection_span(
                f"selection.outerHTML = {repr(highlighted_selection)};")
        else:
            # Highlighting failed.
            # Remove the span tag added by the transform function.
            finalize_selection_span(
                "selection.replaceWith(...selection.childNodes);")

    wrap_and_get_selection(editor.web, random_id, transform_field)
