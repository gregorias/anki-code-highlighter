"""This module handles transformations of note fields."""

from .guard import delete_guarded_snippet, guard_html_comments, prepend_guarded_snippet

__all__ = ["set_up_style_import"]


def set_up_style_import(
    html: str,
    css_assets: list[str],
    guard: str,
) -> str:
    """Adds a guarded stylesheet import block at the beginning of the HTML.

    If a guarded snippet already exists, it is deleted before prepending.

    Args:
        html: The note field HTML content.
        css_assets: The list of CSS files to import.
        guard: The guard string to identify the snippet.

    Returns:
        The modified HTML content with the guarded stylesheet imports.
    """
    guards = guard_html_comments(guard)
    cleaned_html = delete_guarded_snippet(html, guards)

    imports = "".join(f'  @import "{css_asset}";\n' for css_asset in css_assets)
    snippet = f"<style>\n{imports}</style>\n"

    return prepend_guarded_snippet(cleaned_html, snippet, guards)
