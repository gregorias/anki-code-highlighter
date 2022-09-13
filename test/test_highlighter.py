# -*- coding: utf-8 -*-
import unittest

from codehighlighter.bs4extra import encode_soup
from codehighlighter.highlighter import format_code_hljs


class FormatCodeTestCase(unittest.TestCase):

    def test_formats_code(self):
        code_snippet = ("def foo():<br>  return 0")
        expected_html = (
            "<pre style=\"display:flex; justify-content:center;\">" +
            "<code class=\"language-python\">" + "def foo():\n" +
            "  return 0</code></pre>")
        output_html = encode_soup(format_code_hljs('python', code_snippet))
        self.assertEqual(output_html, expected_html)

    def test_formats_nested_code(self):
        code_snippet = ("<div>" + "def foo():<br>  return 0</div>")
        expected_html = (
            "<pre style=\"display:flex; justify-content:center;\">" +
            "<code class=\"language-python\"><div>" + "def foo():\n" +
            "  return 0</div></code></pre>")
        output_html = encode_soup(format_code_hljs('python', code_snippet))
        self.assertEqual(output_html, expected_html)
