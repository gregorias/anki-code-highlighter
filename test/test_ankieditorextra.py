import unittest

from codehighlighter.ankieditorextra import (
    EditorInterface,
    SelectedText,
    UnwrapSelection,
    transform_selection,
)


class MockEditorInterface(EditorInterface):

    def __init__(self, selection_return, note_field_html=""):
        self.highlighted = None
        self.selection_return = selection_return
        self.unwrap_action = None
        self.note_field_html = note_field_html

    def wrap_and_get_selection(self, cb):
        cb(self.selection_return)

    def unwrap_selection(self, action, cb):
        self.unwrap_action = action

    def get_note_field(self, cb):
        cb(self.note_field_html)

    def set_note_field(self, html, cb):
        self.note_field_html = html
        cb(None)


class TransformSelectionTestCase(unittest.TestCase):

    def test_unwraps_on_failed_highlight(self):
        editor = MockEditorInterface(SelectedText("123"))
        err_msg = None

        def on_error(msg):
            nonlocal err_msg
            err_msg = msg

        transform_selection(lambda _: None, editor, on_error)

        self.assertIsNone(err_msg)
        self.assertEqual(UnwrapSelection(), editor.unwrap_action)
