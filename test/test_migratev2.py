import unittest

from codehighlighter.migratev2 import hljs_to_pygments_lang


class MigrateField(unittest.TestCase):
    def test_hljs_to_pygments_lang_for_python(self):
        self.assertEqual(hljs_to_pygments_lang("python"), "Python")

    def test_hljs_to_pygments_lang_for_riscvasm(self):
        # I added riscvasm as a language for Highlight.js, but
        # it's not available in Pygments.
        self.assertEqual(hljs_to_pygments_lang("riscvasm"), None)
