"""Extra functions extending BeautifulSoup."""

import warnings

import bs4
from bs4 import BeautifulSoup

from .html import HtmlString

__all__ = [
    "create_soup",
    "encode_soup",
]


def create_soup(html: HtmlString | None = None) -> bs4.BeautifulSoup:
    """Creates a BeautifulSoup from HTML code."""
    # Using html.parser, because it should be bundled in all Python
    # environments.
    if html:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=bs4.MarkupResemblesLocatorWarning)
            return BeautifulSoup(html, features="html.parser")
    else:
        return BeautifulSoup(features="html.parser")


def encode_soup(tag: bs4.Tag | bs4.BeautifulSoup) -> HtmlString:
    """Encodes an HTML tag or a soup into a valid HTML5 UTF8 string."""
    return HtmlString(str(tag.encode(formatter="html5"), "utf8"))
