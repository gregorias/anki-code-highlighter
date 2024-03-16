from codehighlighter.format import format_selected_code

import unittest


class StubClipboard():

    def __init__(self, stub_text):
        self.stub_text = stub_text

    def text(self):
        return self.stub_text


class FormatSelectedCodeTestCase(unittest.TestCase):

    def test_uses_clipboard_on_empty_selection(self):
        clipboard = StubClipboard("foo")

        self.assertEqual(format_selected_code("", lambda x: x, clipboard),
                         "foo")

    def test_ignores_clipboard_if_code_present(self):
        clipboard = StubClipboard("foo")

        self.assertEqual(format_selected_code("bar", lambda x: x, clipboard),
                         "bar")
