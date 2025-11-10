"""The module for migrating cards to ACH v2."""

from collections.abc import Iterable

import bs4
from anki.collection import Collection
from anki.notes import Note

from . import pygments_highlighter as pygments_highlighter
from .bs4extra import create_soup
from .html import HtmlString, PlainString
from .pygments_highlighter import LexerName, create_block_style, get_lexer_name_by_alias
from .pygments_highlighter import highlight as pygments_highlight

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


def migrate_notes(col: Collection) -> bool:
    """
    Migrates notes from Highlight.js to Pygments.

    Returns:
        Whether all found notes were migrated successfully.
        Unsuccessful notes got tagged with "acherror".
    """
    notes = get_hljs_notes(col)
    all_successful = True
    for note in notes:
        for field_name, field in note.items():
            field_soup = create_soup(HtmlString(field))
            try:
                new_field_soup = migrate_field(field_soup)
            except ValueError:
                note.add_tag("acherror")
                all_successful = False
                continue
            new_field = str(new_field_soup.encode(formatter="minimal"), "utf8")
            note[field_name] = new_field
        col.update_note(note)
    col.flush()
    return all_successful


def migrate_field(field: bs4.BeautifulSoup) -> bs4.BeautifulSoup:
    """
    Migrates HLJS elements to Pygments.

    Raises:
      ValueError: if an error happens.
    """
    try:
        hljs_tags: list[bs4.Tag] = find_hljs_in_field(field)
        for hljs_tag in hljs_tags:
            pygments_tag = migrate_hljs_tag(hljs_tag)
            hljs_tag.replace_with(pygments_tag)
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


class UnknownLanguageError(Exception):
    """Encountered an unknown HLJS language."""

    def __init__(self, language):
        super().__init__()
        self.language = language

    def __str__(self):
        return f"Unknown language: {self.language}."

    def __eq__(self, other):
        if not isinstance(other, UnknownLanguageError):
            return False

        return self.language == other.language

    def __hash__(self):
        return hash(("UnknownLanguageError", self.language))


# TODO: handle possible exceptions in callers including a catch-all.
def migrate_hljs_tag(hljs_pre: bs4.Tag) -> bs4.Tag:
    """Migrates a Highlight.js pre-element to Pygments (class-based, external CSS).

    Raises:
      UnknownLanguageError: if an unknown language was encountered.
    """

    def get_code_tag(hljs_pre: bs4.Tag) -> bs4.Tag:
        code_tag = list(hljs_pre.children)[0]
        assert isinstance(code_tag, bs4.Tag)
        assert code_tag.name == "code"
        return code_tag

    def get_hljs_language(hljs_code: bs4.Tag) -> str:
        classes = hljs_code.attrs["class"]
        language_prefix = "language-"
        languages = [
            c.removeprefix(language_prefix)
            for c in classes
            if c.startswith(language_prefix)
        ]
        assert len(languages) > 0
        return languages[0]

    def get_code_content(hljs_code: bs4.Tag) -> PlainString:
        return PlainString(hljs_code.get_text())

    hljs_code = get_code_tag(hljs_pre)
    hljs_language: str = get_hljs_language(hljs_code)
    pygments_lexer_name: LexerName | None = hljs_to_pygments_lang(hljs_language)

    if pygments_lexer_name is None:
        raise UnknownLanguageError(hljs_language)

    code_content = get_code_content(hljs_code)

    # Highlight the content using Pygments
    highlighted_tag = pygments_highlight(
        code_content, pygments_lexer_name, create_block_style()
    )

    return highlighted_tag
