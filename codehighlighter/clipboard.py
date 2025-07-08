"""Functionalities related to handling a clipboard."""

from typing import Protocol


class Clipboard(Protocol):

    def text(self) -> str:
        pass


class EmptyClipboard(Clipboard):
    """A clipboard that is always empty."""

    def text(self) -> str:
        return ""


class StubClipboard(Clipboard):
    """A clipboard that always returns the stub text."""

    def __init__(self, stub_text):
        self.stub_text = stub_text

    def text(self):
        return self.stub_text
