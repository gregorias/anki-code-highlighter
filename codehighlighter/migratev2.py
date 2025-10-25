"""The module for migrating cards to ACH v2."""

from collections.abc import Iterable

import bs4
from anki.collection import Collection
from anki.notes import Note

from .pygments_highlighter import LexerName, get_lexer_name_by_alias

__all__ = [
    "hljs_to_pygments_lang",
    "migrate_field",
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


def migrate_notes(col: Collection) -> None:
    """
    Migrates notes from Highlight.js to Pygments.

    Returns:
        None
    """
    notes = get_hljs_notes(col)
    for note in notes:
        for _field_name, field in note.items():
            # TODO: Delete before publishing.
            print(f"A found field: {field}.")
    return None


def migrate_field(field: bs4.BeautifulSoup) -> bs4.BeautifulSoup:
    """
    Migrates HLJS elements to Pygments.

    Raises:
      ValueError: if an error happens.
    """
    try:
        hljs_tags: list[bs4.Tag] = find_hljs_in_field(field)
        for _hljs_tag in hljs_tags:
            raise NotImplementedError()
        return field
    except Exception as e:
        raise ValueError("Could not migrate a field.") from e


def find_hljs_in_field(field: bs4.BeautifulSoup) -> list[bs4.Tag]:
    """Finds Highlight.js elements in a field.

    Finds pre-elements with "language-xxx" class.
    """
    pres = field.find_all("pre")
    hljs_pres = [pre for pre in pres if list(pre.select('code[class^="language-"]'))]
    return hljs_pres
