"""The Pygments highlighter.

See DEV.md for more information on the highlighter concept."""

import functools
import re
from collections.abc import Iterable
from typing import NamedTuple, Optional

import bs4

import pygments  # type: ignore
import pygments.formatters  # type: ignore
import pygments.lexer
import pygments.lexers  # type: ignore

from .bs4extra import create_soup
from .html import HtmlString, PlainString
from .pygmentsarm import ArmLexer

LexerName = str
LexerAlias = str


class HtmlStyle(NamedTuple):
    """The style options for Pygments blocks."""

    display_style: str
    block_style: Optional[str]


def create_inline_style() -> HtmlStyle:
    """Creates the inline style options for Pygments code element."""
    return HtmlStyle("inline", block_style=None)


def create_block_style(
    block_style="display:flex; justify-content:center;",
) -> HtmlStyle:
    """Creates the block style options for Pygments code element."""
    return HtmlStyle("block", block_style=block_style)


def remove_spurious_inline_newline(html: str) -> str:
    return re.sub("</span>\n</code>$", "</span></code>", html)


def remove_spurious_inline_spanw(html: str) -> str:
    """Removes the spurious <span class="w"></span> that Pygments inserts."""
    return re.sub('<span class="w"></span>', "", html)


def highlight(code: PlainString, language: LexerName, style: HtmlStyle) -> bs4.Tag:
    """
    Highlights the code snippet with Pygments.

    :param code: A code snippet without HTML markup.
    :param language: A language.
    :param style: The style options to use.
    :return: A BeautifulSoup tag representing the highlighted code.
    """
    lexer = get_lexer_by_name(language)
    if lexer is None:
        # Use the plaintext lexer as a fallback
        lexer = get_plaintext_lexer()
    htmlf = (
        pygments.formatters.get_formatter_by_name("html", nowrap=True)
        if style.display_style == "inline"
        else pygments.formatters.get_formatter_by_name("html")
    )
    highlighted = pygments.highlight(code, lexer, htmlf)
    assert isinstance(highlighted, str)
    highlighted = remove_spurious_inline_spanw(highlighted)

    if style.display_style == "inline":
        highlighted = '<code class="pygments">' + highlighted + "</code>"
        highlighted = remove_spurious_inline_newline(highlighted)
    elif style.display_style == "block":
        highlighted = highlighted.strip()
        highlighted = highlighted.removeprefix('<div class="highlight">')
        highlighted = highlighted.removesuffix("</div>")
        highlighted = highlighted.removeprefix("<pre>")
        highlighted = highlighted.removesuffix("</pre>")
        highlighted = highlighted.removeprefix("<span></span>")
        style_attr = f' style="{style.block_style}"' if style.block_style else ""
        highlighted = (
            f'<div class="pygments"{style_attr}>\n'
            + f'  <pre><code class="nohighlight">{highlighted}</code></pre>\n'
            + "</div>\n"
        )
    return create_soup(HtmlString(highlighted))


@functools.cache
def get_lexer_name_alias_map() -> dict[LexerName, LexerAlias]:
    """Returns a map from a lexer name to its lexer alias."""
    # We need to check if `t[1]` has an element, because not all lexer tuples
    # have this.
    # Deprecated lexers have an empty alias list.
    lexers = {t[0]: t[1][0] for t in pygments.lexers.get_all_lexers() if len(t[1]) >= 1}
    lexers[ArmLexer.name] = ArmLexer.aliases[0]
    return lexers


@functools.cache
def get_lexer_by_name(name: LexerName) -> Optional[pygments.lexer.Lexer]:
    """Returns a lexer by its name.

    pygments.lexers.get_lexer_by_name actually accepts an alias. This function
    corrects this conceptual mismatch.
    """

    name_alias_map = get_lexer_name_alias_map()
    # Treat the name itself as an alias if it is not in the map.
    # This is done to facilitate user manually entering strings like "python"
    # or "cpp".
    alias = name_alias_map.get(name, name)
    if alias == "arm":
        return ArmLexer()
    try:
        return pygments.lexers.get_lexer_by_name(alias)
    except pygments.util.ClassNotFound:
        return None


@functools.cache
def get_lexer_name_by_alias(alias: LexerAlias) -> LexerName | None:
    """Returns a lexer name by its alias."""
    for t in pygments.lexers.get_all_lexers():
        if alias in t[1]:
            return t[0]
    return None


@functools.cache
def get_plaintext_lexer() -> pygments.lexer.Lexer:
    # This should never return None. There’s a unit-test validating this.
    return get_lexer_by_name("output")


@functools.cache
def get_available_languages() -> Iterable[LexerName]:
    """Returns a list of all available languages.

    The languages are in human-readable form, e.g. "C++", not "cpp".
    """
    return get_lexer_name_alias_map().keys()
