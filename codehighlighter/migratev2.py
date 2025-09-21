"""The module for migrating cards to ACH v2."""

from .pygments_highlighter import LexerName, get_lexer_name_by_alias

__all__ = [
    "hljs_to_pygments_lang",
]


def hljs_to_pygments_lang(hljs_lang: str) -> LexerName | None:
    """Translates a HLJS language from an attribute to a Pygments lexer."""
    return get_lexer_name_by_alias(hljs_lang)
