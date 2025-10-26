import unittest

from bs4 import BeautifulSoup, Tag

import codehighlighter.bs4extra as bs4extra
from codehighlighter.html import HtmlString
from codehighlighter.migratev2 import (
    find_hljs_in_field,
    migrate_hljs_tag,
)


def assertHtmlTagEqual(test_case: unittest.TestCase, a: Tag, b: Tag, msg=None):
    if a == b:
        return None

    def format_tag(t: Tag) -> str:
        return t.encode(formatter="html5").decode()

    test_case.assertMultiLineEqual(format_tag(a), format_tag(b), msg)


def extract_pre_from_soup(soup: BeautifulSoup) -> Tag:
    pre_tag = next(x for x in soup.children)
    assert isinstance(pre_tag, Tag), f"Expected a tag but got {type(pre_tag)}."
    return pre_tag


class MigrateField(unittest.TestCase):

    def test_find_hljs_in_field(self):
        html = """
        <pre><code  class="language-python">print("Hello World")</code></pre>
        <pre class="language-javascript">No code-tag here.</pre>
        <pre>No language class here.</pre>
        <div>Some other text</div>
        """

        soup = BeautifulSoup(html, "html.parser")
        result = find_hljs_in_field(soup)

        # Assertions
        self.assertEqual(len(result), 1)
        pre = result[0]
        self.assertEqual(pre.name, "pre")
        code = list(pre.children)[0]
        self.assertEqual(code.name, "code")  # type: ignore
        self.assertEqual(code["class"], ["language-python"])  # type: ignore

    def test_find_hljs_in_field_with_no_targets(self):
        # Test input with no Highlight.js elements
        html_no_hljs = """
        <pre>No language class here</pre>
        <p>Just a paragraph</p>
        """

        soup_no_hljs = BeautifulSoup(html_no_hljs, "html.parser")
        result_no_hljs = find_hljs_in_field(soup_no_hljs)

        # Assertions
        self.assertEqual(len(result_no_hljs), 0)

    def test_migrate_hljs_tag(self):
        soup = bs4extra.create_soup(
            HtmlString(
                """<pre style="display:flex; justify-content:center;"><code class="language-python">def f():
              pass</code></pre>"""
            )
        )

        expected_string = (
            '<div class="pygments" style="display:flex; justify-content:center;">\n'
            + '<pre><code class="nohighlight"><span class="k">def</span><span class="w"> </span><span class="nf">f</span><span class="p">():</span>\n'
            + '              <span class="k">pass</span>\n'
            + "</code></pre>\n"
            + "</div>\n"
        )
        expected = bs4extra.create_soup(HtmlString(expected_string))

        pygments_tag = migrate_hljs_tag(extract_pre_from_soup(soup))

        assertHtmlTagEqual(
            self,
            pygments_tag,
            expected,
            msg="The migrated tag doesn’t look as expected.",
        )
