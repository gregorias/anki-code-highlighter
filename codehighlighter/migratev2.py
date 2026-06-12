"""The module for migrating cards to ACH v2."""

from collections.abc import Iterable

import bs4
from anki.collection import Collection
from anki.notes import Note

from .bs4extra import create_soup
from .html import HtmlString, PlainString
from .pygments_highlighter import LexerName, get_lexer_name_by_alias
from .v2 import pygments_highlighter as v2_pygments_highlighter
from .v2.field import set_up_style_import

__all__ = [
    "hljs_to_pygments_lang",
    "migrate_field",
]

V2_CSS_ASSETS = ["_gch-pygments-solarized.css"]
V2_GUARD = "Greg's Code Highlighter (Add-on 1527277801)"


def get_notes_to_migrate(col: Collection) -> Iterable[Note]:
    """Gets notes that have HLJS, v1 Pygments, or v2 Pygments without styles."""
    # Find all notes that could possibly need migration.
    # Anki supports OR in find_notes.
    note_ids = col.find_notes("pre language- OR pygments OR gch-pygments OR highlight")
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
    elif hljs_lang == "python-repl":
        return "Python console session"
    return get_lexer_name_by_alias(hljs_lang)


def migrate_field_html(field_html: str) -> str:
    """Migrates a note field's HTML to v2 Pygments format."""
    field_soup = create_soup(HtmlString(field_html))
    new_field_soup = migrate_field(field_soup)
    new_field = str(new_field_soup.encode(formatter="minimal"), "utf8")

    # Add or update style-element import if gch-pygments is present
    if "gch-pygments" in new_field:
        new_field = set_up_style_import(new_field, V2_CSS_ASSETS, V2_GUARD)

    return new_field


def migrate_notes(col: Collection) -> bool:
    """
    Migrates notes to v2 Pygments format.

    Returns:
        Whether all found notes were migrated successfully.
        Unsuccessful notes got tagged with "acherror".
    """
    notes = get_notes_to_migrate(col)
    all_successful = True
    for note in notes:
        changed = False
        for field_name, field in note.items():
            try:
                new_field = migrate_field_html(field)
            except ValueError:
                note.add_tag("acherror")
                all_successful = False
                continue

            if new_field != field:
                note[field_name] = new_field
                changed = True

        if changed:
            col.update_note(note)

    col.flush()
    return all_successful


def migrate_field(field: bs4.BeautifulSoup) -> bs4.BeautifulSoup:
    """
    Migrates HLJS and v1 Pygments elements to v2 Pygments.

    Raises:
      ValueError: if an error happens.
    """
    try:
        # Migrate HLJS blocks to v2 Pygments blocks
        hljs_tags: list[bs4.Tag] = find_hljs_in_field(field)
        for hljs_tag in hljs_tags:
            pygments_tag = migrate_hljs_tag(hljs_tag)
            hljs_tag.replace_with(pygments_tag)

        # Update v1 Pygments blocks to use gch-pygments class
        v1_pygments_tags: list[bs4.Tag] = field.find_all(
            class_=["pygments", "highlight"]
        )
        for tag in v1_pygments_tags:
            tag["class"] = [
                c if c not in ("pygments", "highlight") else "gch-pygments"
                for c in tag.get("class", [])
            ]
            # Remove class="nohighlight" from child code element if it exists
            if tag.name == "div":
                code_tag = tag.find("code", class_="nohighlight")
                if code_tag:
                    assert isinstance(code_tag, bs4.Tag)
                    code_tag["class"] = [
                        c for c in code_tag.get("class", []) if c != "nohighlight"
                    ]
                    if not code_tag["class"]:
                        del code_tag["class"]
                else:
                    # Some old Pygments blocks (like those with class="highlight") might be missing <code>
                    pre_tag = tag.find("pre")
                    if pre_tag:
                        assert isinstance(pre_tag, bs4.Tag)
                        inner_code_tag = pre_tag.find("code")
                        if not inner_code_tag:
                            new_code_tag = field.new_tag("code")
                            # Pygments inserts an empty <span></span> at the start, remove it
                            if (
                                pre_tag.contents
                                and isinstance(pre_tag.contents[0], bs4.Tag)
                                and pre_tag.contents[0].name == "span"
                                and not pre_tag.contents[0].contents
                            ):
                                pre_tag.contents[0].extract()
                            new_code_tag.extend(pre_tag.contents)
                            pre_tag.clear()
                            pre_tag.append(new_code_tag)
            elif tag.name == "code":
                # For inline blocks that had class="pygments" directly
                pass

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


def migrate_hljs_tag(hljs_pre: bs4.Tag) -> bs4.Tag:
    """Migrates a Highlight.js pre-element to v2 Pygments.

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

    # Highlight the content using v2 Pygments
    highlighted_tag = v2_pygments_highlighter.highlight(
        code_content, pygments_lexer_name, v2_pygments_highlighter.create_block_style()
    )

    return highlighted_tag
