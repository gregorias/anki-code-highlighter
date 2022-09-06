# -*- coding: utf-8 -*-
from os import path
import pathlib
import unittest

from codehighlighter.bs4extra import encode_soup
from codehighlighter import highlighter


def get_testdata_dir() -> pathlib.Path:
    test_dir = pathlib.Path(path.dirname(path.realpath(__file__)))
    return test_dir / 'testdata'


def read_file(p: pathlib.Path) -> str:
    with open(p, 'r') as f:
        return f.read()


class HighlighterPygmentsTestCase(unittest.TestCase):

    def setUp(self):
        self.testdata_dir = get_testdata_dir()

    def test_highlights_inline_code_to_one_line(self):
        self.assertEqual(
            encode_soup(
                highlighter.format_code_pygments(
                    language='c++',
                    display_style=highlighter.DISPLAY_STYLE.INLINE,
                    code='true')), '<code class="highlight">' +
            '<span class="nb">true</span><span class="w"></span></code>')

    def test_highlights_block_python_code(self):
        input = read_file(self.testdata_dir / "in0.py")
        expected = read_file(self.testdata_dir / "out0.html")
        self.assertEqual(
            encode_soup(
                highlighter.format_code_pygments(
                    language='python',
                    display_style=highlighter.DISPLAY_STYLE.BLOCK,
                    code=input)), expected)
