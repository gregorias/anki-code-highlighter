# -*- coding: utf-8 -*-
import textwrap
import unittest
import warnings

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

    def test_hljs_formatting_doesnt_throw_warnings(self):
        """https://github.com/gregorias/anki-code-highlighter/issues/37"""
        code_snippet = """\
                       template
                       void f(T&amp;&amp; arg) {}

                       void main() {
                         vector v;
                         const vector cv;
                         f(v);            // 1
                         f(cv);           // 2
                         f(std::move(v)); // 3
                       }"""
        code_snippet = textwrap.dedent(code_snippet)
        with warnings.catch_warnings(record=True) as caught_warnings:
            format_code_hljs('cpp', code_snippet)
            self.assertListEqual(caught_warnings, [])
