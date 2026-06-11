import unittest
from textwrap import dedent

from codehighlighter.field import set_up_style_import


class FieldTestCase(unittest.TestCase):

    def test_set_up_style_import_prepends_correctly(self):
        initial_html = "<p>hello world</p>"
        result = set_up_style_import(
            initial_html,
            css_assets=["_gch-pygments-solarized.css"],
            guard="ACH add-on",
        )

        expected = dedent("""\
            <!-- ACH add-on BEGIN -->
            <style>
              @import "_gch-pygments-solarized.css";
            </style>
            <!-- ACH add-on END -->

            <p>hello world</p>""")
        self.assertEqual(result, expected)

    def test_set_up_style_import_replaces_existing(self):
        initial_html = dedent("""\
            <!-- ACH add-on BEGIN -->
            <style>
              @import "old.css";
            </style>
            <!-- ACH add-on END -->

            <p>hello world</p>""")
        result = set_up_style_import(
            initial_html,
            css_assets=["new.css"],
            guard="ACH add-on",
        )

        expected = dedent("""\
            <!-- ACH add-on BEGIN -->
            <style>
              @import "new.css";
            </style>
            <!-- ACH add-on END -->

            <p>hello world</p>""")
        self.assertEqual(result, expected)
