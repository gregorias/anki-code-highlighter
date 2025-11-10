import unittest

from bs4 import BeautifulSoup

from codehighlighter.migratev2 import (
    find_hljs_in_field,
)


class MigrateField(unittest.TestCase):
    def setUp(self):
        self.maxDiff = 10000

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
