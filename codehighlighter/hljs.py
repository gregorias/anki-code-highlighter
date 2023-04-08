# -*- coding: utf-8 -*-
"""The highlight.js highlighter.

Most of the magic of highlight.js happens at runtime. This plugin includes the
necessary JS and CSS files in card templates. This module only wraps the code,
so that the JS scripts can pick it up.

See DEV.md for more information on the highlighter concept."""
from typing import List

import bs4

from .bs4extra import create_soup

__all__ = ['get_available_languages', 'highlight']


def highlight(
        code: str,
        language: str,
        block_style: str = "display:flex; justify-content:center;") -> bs4.Tag:
    """
    Highlights the code snippet with highlight.js.

    :param code: A code snippet without HTML markup.
    :param language: A language.
    :param block_style: The style of the <pre> tag.
    :return: A BeautifulSoup tag representing the highlighted code.
    """
    soup = create_soup()
    code_tag = soup.new_tag('code')
    pre_tag = soup.new_tag('pre')
    pre_tag.append(code_tag)
    code_tag.append(code)

    if language == 'nohighlight':
        code_tag['class'] = [language]
    else:
        code_tag['class'] = ['language-' + language]

    if block_style:
        pre_tag['style'] = block_style

    return pre_tag


def get_available_languages(lang_files: List[str]) -> list[str]:
    """
    Gets a list of available HLJS languages from a list of media files.

    :param lang_files List[str]
    :rtype List[str]
    """
    LANG_PREFIX = '_ch-hljs-lang-'
    LANG_SUFFIX = '.min.js'
    return [
        f.removeprefix(LANG_PREFIX).removesuffix(LANG_SUFFIX)
        for f in lang_files
        if f.startswith(LANG_PREFIX) and f.endswith(LANG_SUFFIX)
    ] + [
        "html",
        "xhtml",
        "rss",
        "atom",
        "xjb",
        "xsd",
        "xsl",
        "plist",
        "wsf",
        "svg",
    ]  # These are handled by xml.min.js.
