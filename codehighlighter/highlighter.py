# -*- coding: utf-8 -*-
"""The main function that highlights the code snippet."""
import enum
from enum import Enum
import html
import re
from typing import List

import bs4  # type: ignore
from bs4 import BeautifulSoup, NavigableString
from .bs4extra import create_soup, replace_br_tags_with_newlines

import os, sys

sys.path.append(os.path.dirname(__file__))
import pygments  # type: ignore
import pygments.formatters  # type: ignore
import pygments.lexers  # type: ignore
# Keep this module Anki agnostic. Only straighforward code operating on HTML.

# This list contains the intended public API of this module.
__all__ = ['format_code_hljs', 'DISPLAY_STYLE'
           'format_code_pygments']


def replace_br(element) -> None:
    if isinstance(element, bs4.Tag) and element.name == 'br':
        element.replace_with('\n')


def walk_func(element) -> list:
    replace_br(element)
    if hasattr(element, 'children'):
        return element.children
    else:
        return []


def walk(soup, func):

    class DfsStack:

        def __init__(self, initial_nodes):
            self.nodes = list(initial_nodes)

        def __iter__(self):
            return self

        def __next__(self):
            if self.nodes:
                top = self.nodes[-1]
                self.nodes.pop()
                return top
            else:
                raise StopIteration()

        def send(self, new_nodes: List[bs4.PageElement]):
            self.nodes.extend(list(new_nodes))

    dfs_stack = DfsStack(soup.children)
    for node in dfs_stack:
        maybe_more_nodes = func(node)
        if maybe_more_nodes:
            dfs_stack.send(maybe_more_nodes)


def format_code_hljs(
        language: str,
        code: str,
        block_style: str = "display:flex; justify-content:center;") -> bs4.Tag:
    """Formats the code snippet.

    Returns:
        A BeautifulSoup tag.
    """
    soup = create_soup(code)
    code_tag = soup.new_tag('code')
    if language == 'nohighlight':
        code_tag['class'] = [language]
    else:
        code_tag['class'] = ['language-' + language]
    pre_tag = soup.new_tag('pre')
    if block_style:
        pre_tag['style'] = block_style
    code_tag.append(soup)
    pre_tag.append(code_tag)
    walk(pre_tag, walk_func)
    return pre_tag


def apply_eye_candy(content: str, language):
    content = re.sub('&lt;-', '←', content)
    content = re.sub('&gt;=', '≥', content)
    content = re.sub('!=', '≠', content)
    content = re.sub('/=', '≠', content)
    content = re.sub(' &gt;&gt; ', ' » ', content)
    content = re.sub('&lt;&lt;', '«', content)
    if language == 'haskell':
        content = re.sub('Bool', '𝔹', content)
        content = re.sub('Integer', 'ℤ', content)
        content = re.sub('Rational', 'ℚ', content)
    return content


def remove_spurious_inline_newline(html: str) -> str:
    return re.sub('</span>\n</code>$', '</span></code>', html)


@enum.unique
class DISPLAY_STYLE(Enum):
    BLOCK = 1
    INLINE = 2


def format_code_pygments(
    language: str,
    display_style: DISPLAY_STYLE,
    code: str,
    block_style: str = "display:flex; justify-content:center;"
) -> bs4.BeautifulSoup:
    code = html.unescape(code)
    lexer = pygments.lexers.get_lexer_by_name(language)
    code = replace_br_tags_with_newlines(code)
    if display_style is DISPLAY_STYLE.INLINE:
        htmlf = pygments.formatters.get_formatter_by_name('html', nowrap=True)
        highlighted = pygments.highlight(code, lexer, htmlf)
        highlighted = '<code class="pygments">' + highlighted + '</code>'
    elif display_style is DISPLAY_STYLE.BLOCK:
        htmlf = pygments.formatters.get_formatter_by_name('html')
        highlighted = pygments.highlight(code, lexer, htmlf)
        highlighted = highlighted.strip()
        highlighted = highlighted.removeprefix('<div class="highlight">')
        highlighted = highlighted.removesuffix('</div>')
        highlighted = highlighted.removeprefix('<pre>')
        highlighted = highlighted.removesuffix('</pre>')
        highlighted = highlighted.removeprefix('<span></span>')
        style_attr = f' style="{block_style}"' if block_style else ""
        highlighted = (f'<div class="pygments"{style_attr}>\n' +
                       f'  <pre><code class="nohighlight">{highlighted}' +
                       '</code></pre>\n</div>\n')
    highlighted = apply_eye_candy(highlighted, language=language)
    if display_style is DISPLAY_STYLE.INLINE:
        highlighted = remove_spurious_inline_newline(highlighted)

    return create_soup(highlighted)
