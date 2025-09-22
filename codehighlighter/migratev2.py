"""The module for migrating cards to ACH v2."""

from collections.abc import Iterable

from anki.collection import Collection
from anki.notes import Note

from .pygments_highlighter import LexerName, get_lexer_name_by_alias

__all__ = [
    "hljs_to_pygments_lang",
]


def get_hljs_notes(col: Collection) -> Iterable[Note]:
    """Gets Highlight.js-like notes."""
    # Highlight.js only uses <pre><code> blocks.
    # The code block has a "language-foo" as a class.
    note_ids = col.find_notes("pre language-")
    return (col.get_note(note_id) for note_id in note_ids)


def hljs_to_pygments_lang(hljs_lang: str) -> LexerName | None:
    """Translates a HLJS language from an attribute to a Pygments lexer."""
    if hljs_lang == "plaintext":
        return "plaintext"
    elif hljs_lang == "armasm":
        return "ARM"
    elif hljs_lang == "riscvasm":
        return "ARM"
    elif hljs_lang == "avrasm":
        return "ARM"
    elif hljs_lang == "x86asm":
        return "NASM"
    elif hljs_lang == "wasm":
        return "WebAssembly"
    elif hljs_lang == "gradle":
        return "Groovy"
    return get_lexer_name_by_alias(hljs_lang)
