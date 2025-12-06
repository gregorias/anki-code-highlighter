"""This module handles guarding strings."""

import re
from typing import Tuple

Guards = Tuple[str, str]


def guard_comments(guard: str, comment_markup: Tuple[str, str]) -> Guards:
    """Creates single-line comment brackets that identify the add-on.

    Args:
        guard: A guard string identifying the add-on.
        comment_markup: The comment symbols.

    Returns:
        The comment brackets.
    """
    return (
        f"{comment_markup[0]} {guard} BEGIN {comment_markup[1]}\n",
        f"{comment_markup[0]} {guard} END {comment_markup[1]}\n",
    )


def guard_html_comments(guard: str) -> Guards:
    """
    Creates HTML comments bracketing import statements.

    Args:
        guard: A guard string used for HTML comments wrapping the imports.

    Returns:
        The comment brackets.
    """
    return guard_comments(guard, ("<!--", "-->"))


def append_guarded_snippet(tmpl: str, snippet: str, guards: Guards) -> str:
    """
    Appends a guarded snippet to a string.

    Args:
        tmpl: The string to modify.
        snippet: The snippet to append.
        guards: The guard strings.

    Returns:
        The modified string.
    """
    GUARD_BEGIN, GUARD_END = guards
    gap = "\n" if tmpl.endswith("\n") else "\n\n"
    return tmpl + gap + GUARD_BEGIN + snippet + GUARD_END


def delete_guarded_snippet(tmpl: str, guards: Guards) -> str:
    """
    Deletes a guarded snippet from a string.

    Args:
        tmpl: The string to modify.
        guards: The guard strings.

    Returns:
        The modified string.
    """
    return re.sub(
        f"(\n)*{re.escape(guards[0])}.*{re.escape(guards[1])}",
        "\n",
        tmpl,
        flags=re.MULTILINE | re.DOTALL,
    )
