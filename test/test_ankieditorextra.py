import unittest

from codehighlighter.ankieditorextra import (
    EditorInterface,
    SelectedText,
    UnwrapSelection,
    transform_selection,
)


class MockEditorInterface(EditorInterface):

    def __init__(self, selection_return):
        self.highlighted = None
        self.selection_return = selection_return
        self.unwrap_action = None

    def wrap_and_get_selection(self, cb):
        cb(self.selection_return)

    def unwrap_selection(self, action, cb):
        self.unwrap_action = action


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
