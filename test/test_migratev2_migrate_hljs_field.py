import unittest

from bs4 import BeautifulSoup, Tag

import codehighlighter.bs4extra as bs4extra
from codehighlighter.html import HtmlString
from codehighlighter.migratev2 import (
    migrate_field,
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


def soupify_str(a: str) -> BeautifulSoup:
    return bs4extra.create_soup(HtmlString(a))


def migrate_hljs_string(field_string):
    """Wraps migrate_field for tests."""
    soup = soupify_str(field_string)
    return migrate_field(soup)


class TestMigrateHljsField(unittest.TestCase):
    def setUp(self):
        self.maxDiff = 2000

    def test_migrate_field_kotlin(self):
        soup = (
            '<pre style="display:flex; justify-content:center;"><code class="language-kotlin">a foo b == Pair(a, b)</code></pre>'
            + '<div style="text-align: center;">An infix operator that creates a pair.</div>'
        )

        expected = soupify_str(
            '<div class="pygments" style="display:flex; justify-content:center;">\n'
            + '<pre><code class="nohighlight"><span class="n">a</span><span class="w"> </span><span class="n">foo</span><span class="w"> </span><span class="n">b</span><span class="w"> </span><span class="o">==</span><span class="w"> </span><span class="n">Pair</span><span class="p">(</span><span class="n">a</span><span class="p">,</span><span class="w"> </span><span class="n">b</span><span class="p">)</span>\n'
            + "</code></pre>\n"
            + "</div>\n"
            + '<div style="text-align: center;">An infix operator that creates a pair.</div>'
        )

        pygments_tag = migrate_hljs_string(soup)

        assertHtmlTagEqual(
            self,
            pygments_tag,
            expected,
            msg="The migrated field doesn’t look as expected.",
        )

    def test_migrate_field_kotlin_with_multiple_code_blocks(self):
        soup = (
            '<pre style="display:flex; justify-content:center;"><code class="language-kotlin">a foo b == Pair(a, b)</code></pre>'
            + '<div style="text-align: center;">An infix operator that creates a pair.</div>'
            + '<pre style="display:flex; justify-content:center;"><code class="language-kotlin">a foo b == Pair(a, b)</code></pre>'
        )

        expected = soupify_str(
            '<div class="pygments" style="display:flex; justify-content:center;">\n'
            + '<pre><code class="nohighlight"><span class="n">a</span><span class="w"> </span><span class="n">foo</span><span class="w"> </span><span class="n">b</span><span class="w"> </span><span class="o">==</span><span class="w"> </span><span class="n">Pair</span><span class="p">(</span><span class="n">a</span><span class="p">,</span><span class="w"> </span><span class="n">b</span><span class="p">)</span>\n'
            + "</code></pre>\n"
            + "</div>\n"
            + '<div style="text-align: center;">An infix operator that creates a pair.</div>'
            '<div class="pygments" style="display:flex; justify-content:center;">\n'
            + '<pre><code class="nohighlight"><span class="n">a</span><span class="w"> </span><span class="n">foo</span><span class="w"> </span><span class="n">b</span><span class="w"> </span><span class="o">==</span><span class="w"> </span><span class="n">Pair</span><span class="p">(</span><span class="n">a</span><span class="p">,</span><span class="w"> </span><span class="n">b</span><span class="p">)</span>\n'
            + "</code></pre>\n"
            + "</div>\n"
        )

        pygments_tag = migrate_hljs_string(soup)

        assertHtmlTagEqual(
            self,
            pygments_tag,
            expected,
            msg="The migrated field doesn’t look as expected.",
        )
