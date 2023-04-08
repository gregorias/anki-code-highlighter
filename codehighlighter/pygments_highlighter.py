# -*- coding: utf-8 -*-
"""The Pygments highlighter.

See DEV.md for more information on the highlighter concept."""
from dataclasses import dataclass
import re
from typing import NamedTuple, Optional

import bs4

from .bs4extra import create_soup

import pygments  # type: ignore
import pygments.formatters  # type: ignore
import pygments.lexers  # type: ignore


class HtmlStyle(NamedTuple):
    """The style options for Pygments blocks."""
    display_style: str
    block_style: Optional[str]


def create_inline_style() -> HtmlStyle:
    """Creates the inline style options for Pygments code element."""
    return HtmlStyle("inline", block_style=None)


def create_block_style(
        block_style="display:flex; justify-content:center;") -> HtmlStyle:
    """Creates the block style options for Pygments code element."""
    return HtmlStyle("block", block_style=block_style)


def remove_spurious_inline_newline(html: str) -> str:
    return re.sub('</span>\n</code>$', '</span></code>', html)


def highlight(code: str, language: str, style: HtmlStyle) -> bs4.Tag:
    """
    Highlights the code snippet with Pygments.

    :param code: A code snippet without HTML markup.
    :param language: A language.
    :param style: The style options to use.
    :return: A BeautifulSoup tag representing the highlighted code.
    """
    lexer = pygments.lexers.get_lexer_by_name(language)
    htmlf = pygments.formatters.get_formatter_by_name(
        'html', nowrap=True
    ) if style.display_style == "inline" else pygments.formatters.get_formatter_by_name(
        'html')
    highlighted = pygments.highlight(code, lexer, htmlf)

    if style.display_style == "inline":
        highlighted = '<code class="pygments">' + highlighted + '</code>'
        highlighted = remove_spurious_inline_newline(highlighted)
    elif style.display_style == "block":
        highlighted = highlighted.strip()
        highlighted = highlighted.removeprefix('<div class="highlight">')
        highlighted = highlighted.removesuffix('</div>')
        highlighted = highlighted.removeprefix('<pre>')
        highlighted = highlighted.removesuffix('</pre>')
        highlighted = highlighted.removeprefix('<span></span>')
        style_attr = f' style="{style.block_style}"' if style.block_style else ""
        highlighted = (
            f'<div class="pygments"{style_attr}>\n' +
            f'  <pre><code class="nohighlight">{highlighted}</code></pre>\n' +
            '</div>\n')
    return create_soup(highlighted)


def get_available_languages() -> list[str]:
    # Filter out lexers with spaces in their name, because
    # get_lexer_by_name can't find them. Lexers with spaces are niche
    # anyway.
    return [t[0] for t in pygments.lexers.get_all_lexers() if ' ' not in t[0]]
