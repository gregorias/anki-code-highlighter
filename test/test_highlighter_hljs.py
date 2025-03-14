import textwrap
import unittest
import warnings

from codehighlighter import ankieditorextra, hljs, hljslangs

cpp = hljslangs.Language(name='C++', alias='cpp')
python = hljslangs.Language(name='Python', alias='python')


class HighlighterHljsTestCase(unittest.TestCase):

    def test_higlights_code(self):
        code = ("def foo():\n" + "  return 0")
        expected = ("<pre style=\"display:flex; justify-content:center;\">" +
                    "<code class=\"language-python\">" + "def foo():\n" +
                    "  return 0</code></pre>")

        result = ankieditorextra.highlight_selection(
            code, lambda code: hljs.highlight(code, python))
        self.assertEqual(result, expected)

    def test_hljs_doesnt_throw_warnings(self):
        """https://github.com/gregorias/anki-code-highlighter/issues/37"""
        code = """\
               template
               void f(T&& arg) {}

               void main() {
                 vector v;
                 const vector cv;
                 f(v);            // 1
                 f(cv);           // 2
                 f(std::move(v)); // 3
               }"""
        code = textwrap.dedent(code)
        with warnings.catch_warnings(record=True) as caught_warnings:
            ankieditorextra.highlight_selection(
                code, lambda code: hljs.highlight(code, cpp))
            self.assertListEqual(caught_warnings, [])
