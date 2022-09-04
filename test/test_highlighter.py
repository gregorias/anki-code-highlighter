# -*- coding: utf-8 -*-
import unittest

from codehighlighter.highlighter import format_code


class FormatCodeTestCase(unittest.TestCase):

    def test_formats_code(self):
        input_html = ("<pre><code id=\"foobar123\">" + "def foo():<br>" +
                      "  return 0</code></pre>")
        expected_html = ("<pre><code class=\"language-python\">" +
                         "def foo():\n" + "  return 0</code></pre>")
        output_html = format_code("foobar123", 'language-python', input_html)
        self.assertEqual(output_html, expected_html)
