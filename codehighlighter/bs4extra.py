# -*- coding: utf-8 -*-
""" Extra functions extending BeautifulSoup."""
from typing import Union
import bs4

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
