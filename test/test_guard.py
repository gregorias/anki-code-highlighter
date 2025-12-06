import unittest
from textwrap import dedent

from codehighlighter.guard import (
    append_guarded_snippet,
    delete_guarded_snippet,
    guard_comments,
)


class AssetsGuardTestCase(unittest.TestCase):

    def test_guard_comments(self):
        self.assertEqual(
            guard_comments("Add-on", ("/*", "*/")),
            ("/* Add-on BEGIN */\n", "/* Add-on END */\n"),
        )

    def test_append_appends_with_gap(self):
        self.assertEqual(
            append_guarded_snippet(
                "{{Cloze}}",
                "Foo\nBar\n",
                ("<!-- Foo BEGIN -->\n", "<!-- Foo END -->\n"),
            ),
            dedent(
                """\
            {{Cloze}}

            <!-- Foo BEGIN -->
            Foo
            Bar
            <!-- Foo END -->
            """
            ),
        )

    def test_delete_deletes_guarded_snippet(self):
        TMPL = dedent(
            """\
            {{Cloze}}

            <!-- Foo BEGIN -->
            <link rel="stylesheet" href="c.css" class="plugin">
            <script src="j.js" class="plugin"></script>
            <!-- Foo END -->
            """
        )
        self.assertEqual(
            delete_guarded_snippet(
                TMPL, ("<!-- Foo BEGIN -->\n", "<!-- Foo END -->\n")
            ),
            "{{Cloze}}\n",
        )

    def test_delete_deletes_too_many_newlines(self):
        TMPL = dedent(
            """\
            {{Cloze}}


            <!-- Foo BEGIN -->
            <link rel="stylesheet" href="c.css" class="plugin">
            <script src="j.js" class="plugin"></script>
            <!-- Foo END -->
            """
        )
        self.assertEqual(
            delete_guarded_snippet(
                TMPL, ("<!-- Foo BEGIN -->\n", "<!-- Foo END -->\n")
            ),
            "{{Cloze}}\n",
        )
