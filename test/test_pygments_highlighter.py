import unittest

from codehighlighter.html import PlainString
from codehighlighter.pygments_highlighter import (
    SUPPORTED_LEXERS,
    create_inline_style,
    get_lexer_name_alias_map,
    highlight,
)


class PygmentsHighlighterTestCase(unittest.TestCase):
    def test_supported_lexers_are_subset_of_all_lexers(self):
        all_lexers = set(get_lexer_name_alias_map().keys())
        supported_lexers = set(SUPPORTED_LEXERS)
        self.assertTrue(supported_lexers.issubset(all_lexers))

    def test_arm_lexer(self):
        # Test that the ARM lexer works and is correctly picked up by
        # the highlighter.
        code = PlainString("mov  r1, r0")
        result = (
            highlight(code, "ARM", create_inline_style())
            .encode(formatter="html5")
            .decode()
        )
        self.assertEqual(
            result,
            '<code class="pygments">'
            + '<span class="nf">mov</span>'
            + '<span class="w"> </span><span class="no">r1</span><span class="p">,</span><span class="w"> </span><span class="no">r0</span>'
            + "</code>",
        )
