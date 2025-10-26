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
            field_soup = create_soup(HtmlString(field))
            try:
                new_field_soup = migrate_field(field_soup)
            except ValueError:
                # TODO: handle this case
                continue
            new_field = str(new_field_soup.encode(formatter="minimal"), "utf8")
            print(f"The new field is: {new_field}.")
            # note[field_name] = new_field
    # col.update_notes(notes)
    return None


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
            field = replace_tag(hljs_tag, pygments_tag)
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


def migrate_hljs_tag(hljs_pre: bs4.Tag) -> bs4.Tag:
    """Migrates a Highlight.js pre-element to Pygments (class-based, external CSS)."""

    def get_code_tag(hljs_pre: bs4.Tag) -> bs4.Tag:
        code_tag = list(hljs_pre.children)[0]
        assert isinstance(code_tag, bs4.Tag)
        assert code_tag.name == "code"
        return code_tag

    def get_hljs_language(hljs_code: bs4.Tag) -> str:
        classes = hljs_code.attrs["class"]
        language_prefix = "language-"
        for c in classes:
            if c.startswith(language_prefix):
                return c.removeprefix(language_prefix)
        raise ValueError("Could not find the language class in the tag.")

    def get_code_content(hljs_code: bs4.Tag) -> PlainString:
        return PlainString(hljs_code.get_text())

    hljs_code = get_code_tag(hljs_pre)
    hljs_language: str = get_hljs_language(hljs_code)
    pygments_lexer_name: LexerName | None = hljs_to_pygments_lang(hljs_language)

    # TODO: If a proper replacement language could not be found.
    # Fall back to an UI for selecting it.
    if pygments_lexer_name is None:
        raise ValueError(f"Could not a proper Pygments lexer for {hljs_language}.")

    code_content = get_code_content(hljs_code)

    # Highlight the content using Pygments
    highlighted_tag = pygments_highlight(
        code_content, pygments_lexer_name, create_block_style()
    )

    return highlighted_tag


def replace_tag(_src: bs4.Tag, _dest: bs4.Tag) -> bs4.BeautifulSoup:
    """Replaces the source tag with the destination tag."""
    raise NotImplementedError()
