import random
import typing
from dataclasses import dataclass
from typing import Callable, Optional, Union

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


@dataclass
class SelectedText:
    text: PlainString


class SelectionException:
    pass


class NoSelectionException(SelectionException):
    pass


class PartialSelectionException(SelectionException):
    pass


@dataclass
class UnknownSelectionException(SelectionException):
    message: str


def wrap_and_get_selection(
        webview: aqt.editor.EditorWebView, wrap_id: str,
        cb: Callable[[Union[SelectedText, SelectionException]], None]) -> None:
    """
    Wraps a field selection in a span tag and returns the selected text.
    """
    failed_to_find_selection = 'Failed to find a selection.'

    def handle_result(result):

        def safe_get(d, key):
            if isinstance(d, dict):
                return d.get(key)
            return None

        selected_text = safe_get(result, 'selectionText')
        if selected_text is not None:
            cb(SelectedText(text=selected_text))
            return None

        error = safe_get(result, 'error')
        message = safe_get(error, 'message')
        if message == failed_to_find_selection:
            cb(NoSelectionException())
        elif message == ("Failed to execute 'surroundContents' on 'Range': " +
                         "The Range has partially selected a non-Text node."):
            # make sure this error message is clear
            # (https://github.com/gregorias/anki-code-highlighter/issues/60)
            cb(PartialSelectionException())
        else:
            cb(UnknownSelectionException(message=str(error)))

        return None

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
        """, handle_result)


@dataclass
class UnwrapSelection:
    pass


@dataclass
class ReplaceWrapSelection:
    contents: HtmlString


def unwrap_selection(webview: aqt.editor.EditorWebView, wrap_id: str,
                     action: Union[UnwrapSelection,
                                   ReplaceWrapSelection], cb) -> None:
    """Unwraps the span tag created by `wrap_and_get_selection`.
    """

    if isinstance(action, UnwrapSelection):
        action_js = "selection.replaceWith(...selection.childNodes);"
    elif isinstance(action, ReplaceWrapSelection):
        action_js = f"selection.outerHTML = {action.contents};"

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
        webview, f"""
         let selection = document.activeElement.shadowRoot.getElementById({wrap_id});
         // A hack against spurious br-tags that get inserted by the Anki editor.
         // https://github.com/gregorias/anki-code-highlighter/issues/51
         if (selection.nextElementSibling?.tagName === "BR" && selection.nextElementSibling.nextSibling === null) {{
             selection.nextElementSibling.remove();
         }}
         {action_js}
         return null;""", cb)


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
def transform_selection(webview: aqt.editor.EditorWebView,
                        highlight: Callable[[PlainString], Optional[bs4.Tag]],
                        onError: Callable[[str], typing.Any]) -> None:
    """
    Transforms selected text using `transform`.

    :param editor aqt.editor.Editor
    :param highlight Callable[[str], bs4.Tag]:
        The highlighting function that receives code snippets and returns HTML
        with highlighting information.
    :param onError Callable[[str], typing.Any]:
        The callback function that is called if an unrecoverable error has
        occurred. Provides an error message.
    :rtype None
    """
    random_id = str(random.randint(0, 10000))

    def transform_field(
            selection_return: Union[SelectedText, SelectionException]) -> None:

        if isinstance(selection_return, SelectionException):
            if isinstance(selection_return, NoSelectionException):
                onError("Failed to find a code selection to highlight." +
                        " You need to select a code snippet or at least a " +
                        "field before triggerring the highlight action.")
            elif isinstance(selection_return, PartialSelectionException):
                # Make sure this error message is clear
                # (https://github.com/gregorias/anki-code-highlighter/issues/60)
                onError(
                    "The selection splits an HTML node, which prevents the " +
                    "highlighting plugin from proceeding.\n" +
                    "Make sure that you select entire HTML elements, e.g., " +
                    "if your code is `<span>hello</span>world`, don’t select" +
                    " just `ello</span>world`.\n" +
                    "You can refactor your code snippet in the HTML editor " +
                    "(https://docs.ankiweb.net/editing.html#editing-features)"
                    + " before highlighting.")
            elif isinstance(selection_return, UnknownSelectionException):
                onError(
                    "An unknown transformation error has occurred " +
                    f"({selection_return.message}). " +
                    " Report it to the developer at " +
                    "https://github.com/gregorias/anki-code-highlighter/issues/new."
                )
            else:
                onError(
                    "An unknown transformation error has occurred " +
                    f"({str(selection_return)}). " +
                    " Report it to the developer at " +
                    "https://github.com/gregorias/anki-code-highlighter/issues/new."
                )
            return None

        highlighted_selection = highlight_selection(selection_return.text,
                                                    highlighter=highlight)
        if highlighted_selection:
            unwrap_selection(
                webview, random_id,
                ReplaceWrapSelection(
                    contents=HtmlString(repr(highlighted_selection))),
                lambda _: None)
        else:
            # Highlighting failed.
            # Remove the span tag added by the transform function.
            unwrap_selection(webview, random_id, UnwrapSelection(),
                             lambda _: None)

    wrap_and_get_selection(webview, random_id, transform_field)
