import unittest

from codehighlighter.html import PlainString
from codehighlighter.pygments_highlighter import create_inline_style, highlight


class PygmentsHighlighterTestCase(unittest.TestCase):

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
