import unittest
from textwrap import dedent

from codehighlighter.guard import (
    delete_guarded_snippet,
    guard_comments,
    prepend_guarded_snippet,
)


class AssetsGuardTestCase(unittest.TestCase):

    def test_guard_comments(self):
        self.assertEqual(
            guard_comments("Add-on", ("/*", "*/")),
            ("/* Add-on BEGIN */\n", "/* Add-on END */\n"),
        )

    def test_prepend_prepends_with_gap(self):
        self.assertEqual(
            prepend_guarded_snippet(
                "body {}", "Foo\nBar\n", ("<!-- Foo BEGIN -->\n", "<!-- Foo END -->\n")
            ),
            dedent(
                """\
            <!-- Foo BEGIN -->
            Foo
            Bar
            <!-- Foo END -->

            body {}"""
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

    def test_delete_deletes_all_surrounding_newlines(self):
        TMPL = dedent(
            """\
           {{Cloze}}

           <!-- Foo BEGIN -->
           <link rel="stylesheet" href="c.css" class="plugin">
           <script src="j.js" class="plugin"></script>
           <!-- Foo END -->

           {{Foo}}
           """
        )
        self.assertEqual(
            delete_guarded_snippet(
                TMPL, ("<!-- Foo BEGIN -->\n", "<!-- Foo END -->\n")
            ),
            "{{Cloze}}\n{{Foo}}\n",
        )

    def test_delete_deletes_prefix_newlines(self):
        TMPL = dedent(
            """\
               <!-- Foo BEGIN -->
               <link rel="stylesheet" href="c.css" class="plugin">
               <script src="j.js" class="plugin"></script>
               <!-- Foo END -->

               {{Foo}}
               """
        )
        self.assertEqual(
            delete_guarded_snippet(
                TMPL, ("<!-- Foo BEGIN -->\n", "<!-- Foo END -->\n")
            ),
            "{{Foo}}\n",
        )
