import unittest

from bs4 import BeautifulSoup, Tag

import codehighlighter.bs4extra as bs4extra
from codehighlighter.html import HtmlString
from codehighlighter.migratev2 import (
    UnknownLanguageError,
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


def soupify_str(a: str) -> BeautifulSoup:
    return bs4extra.create_soup(HtmlString(a))


def migrate_hljs_string(tag_string):
    """Wraps migrate_hljs_tag for tests."""
    soup = soupify_str(tag_string)
    return migrate_hljs_tag(extract_pre_from_soup(soup))


class TestMigrateHljsTag(unittest.TestCase):
    def test_migrate_hljs_tag_python(self):
        soup = (
            '<pre style="display:flex; justify-content:center;"><code class="language-python">def f():\n'
            + "  pass</code></pre>"
        )

        expected = soupify_str(
            '<div class="pygments" style="display:flex; justify-content:center;">\n'
            + '<pre><code class="nohighlight"><span class="k">def</span><span class="w"> </span><span class="nf">f</span><span class="p">():</span>\n'
            + '  <span class="k">pass</span>\n'
            + "</code></pre>\n"
            + "</div>\n"
        )

        pygments_tag = migrate_hljs_string(soup)

        assertHtmlTagEqual(
            self,
            pygments_tag,
            expected,
            msg="The migrated tag doesn’t look as expected.",
        )

    def test_migrate_hljs_tag_no_lang_class(self):
        soup = '<pre><code class="language-arm">mov</code></pre>'

        with self.assertRaises(UnknownLanguageError):
            migrate_hljs_string(soup)
