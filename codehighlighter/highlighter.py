# -*- coding: utf-8 -*-
"""The main function that highlights the code snippet."""
from typing import List

import bs4  # type: ignore
from bs4 import BeautifulSoup, NavigableString
# Keep this module Anki agnostic. Only straighforward code operating on HTML.

# This list contains the intended public API of this module.
__all__ = ['format_code']


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
