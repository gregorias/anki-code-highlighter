# -*- coding: utf-8 -*-
"""The main function that highlights the code snippet."""
import enum
from enum import Enum
import re
from typing import List

import bs4  # type: ignore
from bs4 import BeautifulSoup, NavigableString

import os, sys

sys.path.append(os.path.dirname(__file__))
import pygments  # type: ignore
import pygments.formatters  # type: ignore
import pygments.lexers  # type: ignore
# Keep this module Anki agnostic. Only straighforward code operating on HTML.

# This list contains the intended public API of this module.
__all__ = ['format_code', 'DISPLAY_STYLE'
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


def format_code(language: str, code: str) -> bs4.Tag:
    """Formats the code snippet.

    Returns:
        A BeautifulSoup tag.
    """
    soup = BeautifulSoup(code, features='html.parser')
    code_tag = soup.new_tag('code')
    code_tag['class'] = [language]
    pre_tag = soup.new_tag('pre')
    pre_tag['style'] = "display:flex; justify-content:center;"
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


def format_code_pygments(language: str, display_style: DISPLAY_STYLE,
                         code: str) -> bs4.BeautifulSoup:
    lexer = pygments.lexers.get_lexer_by_name(language)
    if display_style is DISPLAY_STYLE.INLINE:
        htmlf = pygments.formatters.get_formatter_by_name('html', nowrap=True)
        highlighted = pygments.highlight(code, lexer, htmlf)
        highlighted = '<code class="highlight">' + highlighted + '</code>'
    elif display_style is DISPLAY_STYLE.BLOCK:
        htmlf = pygments.formatters.get_formatter_by_name('html')
        highlighted = pygments.highlight(code, lexer, htmlf)
        highlighted = highlighted.strip()
        highlighted = highlighted.removeprefix('<div class="highlight">')
        highlighted = highlighted.removesuffix('</div>')
        highlighted = highlighted.removeprefix('<pre>')
        highlighted = highlighted.removesuffix('</pre>')
        highlighted = highlighted.removeprefix('<span></span>')
        highlighted = (
            f'<div class="pygments" style="display:flex; justify-content:center;">\n  <pre><code class="nohighlight">{highlighted}'
            + '</code></pre>\n</div>\n')
    highlighted = apply_eye_candy(highlighted, language=language)
    if display_style is DISPLAY_STYLE.INLINE:
        highlighted = remove_spurious_inline_newline(highlighted)

    return BeautifulSoup(highlighted, features='html.parser')
