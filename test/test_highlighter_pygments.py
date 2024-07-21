# -*- coding: utf-8 -*-
import pathlib
import unittest
from os import path

import pygments.lexer
import pygments.lexers
from codehighlighter import ankieditorextra, pygments_highlighter
from codehighlighter.pygments_highlighter import create_block_style, create_inline_style


def get_testdata_dir() -> pathlib.Path:
    test_dir = pathlib.Path(path.dirname(path.realpath(__file__)))
    return test_dir / 'testdata'


def read_file(p: pathlib.Path) -> str:
    with open(p, 'r') as f:
        return f.read()


class HighlighterPygmentsTestCase(unittest.TestCase):

    def setUp(self):
        self.testdata_dir = get_testdata_dir()

    def test_all_lexer_names_lead_to_a_lexer(self):
        for language in pygments_highlighter.get_available_languages():
            lexer = pygments_highlighter.get_lexer_by_name(language)
            self.assertIsInstance(lexer, pygments.lexer.Lexer)

    def test_get_lexer_by_name_also_works_with_aliases(self):
        lexer = pygments_highlighter.get_lexer_by_name('cpp')
        self.assertEqual(lexer.name, 'C++')

    def test_get_lexer_by_name_return_none_on_bogus_name(self):
        lexer = pygments_highlighter.get_lexer_by_name('doesnotexist')
        self.assertIsNone(lexer)

    def test_get_plaintext_lexer_returns_a_lexer(self):
        lexer = pygments_highlighter.get_plaintext_lexer()
        self.assertEqual(lexer.name, 'Text output')

    def test_highlights_using_plaintext_on_bogus_language_name(self):
        result = ankieditorextra.highlight_selection(
            'true', lambda code: pygments_highlighter.highlight(
                code, 'doesnotexist', create_inline_style()))

        self.assertEqual(
            result, '<code class="pygments">' +
            '<span class="go">true</span>' + '</code>')

    def test_highlights_inline_code_to_one_line(self):
        result = ankieditorextra.highlight_selection(
            'true', lambda code: pygments_highlighter.highlight(
                code, 'C++', create_inline_style()))

        self.assertEqual(
            result, '<code class="pygments">' +
            '<span class="nb">true</span>' + '</code>')

    def test_highlights_block_python_code(self):
        input = read_file(self.testdata_dir / "in0.py")
        expected = read_file(self.testdata_dir / "out0.html")
        result = ankieditorextra.highlight_selection(
            input, lambda code: pygments_highlighter.highlight(
                code, 'Python', create_block_style()))
        self.assertEqual(result, expected)

    def test_highlights_block_html_code(self):
        input = read_file(self.testdata_dir / "in1.html")
        expected = read_file(self.testdata_dir / "out1.html")
        result = ankieditorextra.highlight_selection(
            input, lambda code: pygments_highlighter.highlight(
                code, 'Python', create_block_style()))
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
                code, 'Python', create_block_style()))
        self.assertEqual(result, expected)
