# -*- coding: utf-8 -*-
from os import path
import pathlib
import unittest

from codehighlighter.bs4extra import encode_soup
from codehighlighter import ankieditorextra
from codehighlighter import pygments_highlighter
from codehighlighter.pygments_highlighter import create_inline_style, create_block_style


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
        result = ankieditorextra.highlight_selection(
            'true', lambda code: pygments_highlighter.highlight(
                code, 'c++', create_inline_style()))

        self.assertEqual(
            result, '<code class="pygments">' +
            '<span class="nb">true</span>' + '</code>')

    def test_highlights_block_python_code(self):
        input = read_file(self.testdata_dir / "in0.py")
        expected = read_file(self.testdata_dir / "out0.html")
        result = ankieditorextra.highlight_selection(
            input, lambda code: pygments_highlighter.highlight(
                code, 'python', create_block_style()))
        self.assertEqual(result, expected)

    def test_highlights_block_html_code(self):
        input = read_file(self.testdata_dir / "in1.html")
        expected = read_file(self.testdata_dir / "out1.html")
        result = ankieditorextra.highlight_selection(
            input, lambda code: pygments_highlighter.highlight(
                code, 'python', create_block_style()))
        self.assertEqual(result, expected)

    def test_removes_html_entities(self):
        code_snippet = ("def foo():<br>&nbsp; return 0")
        expected = (
            '<div class="pygments" style="display:flex; justify-content:center;">\n'
            +
            '<pre><code class="nohighlight"><span class="k">def</span> <span class="nf">foo</span><span class="p">():</span>\n'
            + '  <span class="k">return</span> <span class="mi">0</span>\n' +
            '</code></pre>\n' + '</div>\n')
        result = ankieditorextra.highlight_selection(
            code_snippet, lambda code: pygments_highlighter.highlight(
                code, 'python', create_block_style()))
        self.assertEqual(result, expected)
