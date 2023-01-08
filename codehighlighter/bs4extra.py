# -*- coding: utf-8 -*-
""" Extra functions extending BeautifulSoup."""
from typing import Union
import bs4
from bs4 import BeautifulSoup

__all__ = [
    'encode_soup',
]


def encode_soup(tag: Union[bs4.Tag, bs4.BeautifulSoup]) -> str:
    """
    Encodes an HTML tag or a soup into a valid HTML5 UTF8 string.

    :param tag Union[bs4.Tag, bs4.BeautifulSoup]
    :rtype str: HTML5 UTF8 string
    """
    return str(tag.encode(formatter='html5'), 'utf8')


def replace_br_tags_with_newlines(html: str) -> str:
    """
    Replaces <br> with "\n"

    :param node str: HTML code
    :rtype str: Reformatted HTML code
    """
    soup = BeautifulSoup(html, features='html.parser')
    for br in soup.find_all('br'):
        br.replace_with('\n')
    return encode_soup(soup)
