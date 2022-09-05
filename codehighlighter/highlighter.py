# -*- coding: utf-8 -*-
"""The main function that highlights the code snippet."""
from typing import List

import bs4
from bs4 import BeautifulSoup, NavigableString
# Keep this module Anki agnostic. Only straighforward code operating on HTML.

# This list contains the intended public API of this module.
__all__ = ['format_code']


def replace_br(element: bs4.PageElement) -> None:
    if isinstance(element, bs4.Tag) and element.name == 'br':
        element.replace_with('\n')


def walk(soup: bs4.BeautifulSoup, func):

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


def format_code(random_id: str, language: str, html: str) -> str:
    """Formats the just created code element.

    Returns:
        An HTML5-encoded string.
    """
    soup = BeautifulSoup(html, features='html.parser')
    for code_node in soup.find_all(id=random_id):
        del code_node['id']
        code_node['class'] = [language]
        walk(code_node, replace_br)
    return str(soup.encode(formatter='html5'), 'utf8')
