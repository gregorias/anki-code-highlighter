"""Generates the CSS for Pygments highlighting."""

# The style sheet consists of 2 sections:
#
# 1. Preamble, which describes the surounding box and background.
# 2. Tokens, which describes the individual tokens. The meaning of a token is
#    consistent with Pygments.
#
# Using plain string manipulation instead of cssutils, because
# cssutils 2.15 can't parse ':is(.foo, .bar)' selector that I use.

import textwrap

import pygments
import pygments.formatters
import pygments.formatters.html
import pygments.style
import pygments.styles

DAY_STYLE = "solarized-light"
NIGHT_STYLE = "solarized-dark"
SOLARIZED_LIGHT_BORDER_COLOR = "#cdbc84"
SOLARIZED_DARK_BORDER_COLOR = "#052831"
PYGMENTS_CLASS = "gch-pygments"
# Using multiple night mode classes to accommodate different environments.
# Anki's live editor uses ".nightMode," while AnkiDroid's renderer uses
# ".night_mode," for instance.
NIGHT_MODE_SELECTOR = ":is(.night_mode,.night-mode,.nightMode)"
DAY_MODE_SELECTOR_STR = f".{PYGMENTS_CLASS}"
NIGHT_MODE_SELECTOR_STR = f"{NIGHT_MODE_SELECTOR} .{PYGMENTS_CLASS}"


def delete_pygments_css_preamble(pygments_css: str, prefix_selector: str) -> str:
    """Deletes code block styles.

    This plugin defines its own style for code blocks, so we don't want to keep
    the default Pygments styles.

    Arguments:
        pygments_css_rules: The list of CSS rules to delete the preamble from.
        prefix_selector: The CSS selector that prefixes all Pygments rules.
    """
    # As 2026 Pygments, the preamble ends with a rule like this:
    # :is(.night_mode, .night-mode,.nightMode) .gch-pygments { background: #002b36; color: #839496 }
    # And later only is followed up by token rules:
    # :is(.night_mode, .night-mode, .nightMode) .gch-pygments .c { color: #586E75; font-style: italic } /* Comment */
    # So we delete lines until we reach token rules.
    pygments_css_lines = pygments_css.splitlines()
    # Find the last line.
    preamble_end_index = None
    for i, line in enumerate(pygments_css_lines):
        if line.startswith(prefix_selector + " { background"):
            preamble_end_index = i
            break
    if preamble_end_index is None:
        raise ValueError("Could not find the end of the Pygments CSS preamble.")
    return "\n".join(pygments_css_lines[preamble_end_index + 1 :])


# Using str for the selector, because that's how Pygments likes it.
def get_pygments_token_css(style: pygments.style.Style, prefix_selector: str) -> str:
    """Gets the CSS of a particular Pygments style without the preamble.

    Arguments:
      prefix_selector: The CSS selector to prefix all Pygments rules with.
    """
    # In the context of this plugin, only the HTML formatter is used.
    html_formatter: pygments.formatters.html.HtmlFormatter = (
        pygments.formatters.get_formatter_by_name("html", style=style)
    )
    pygments_css = html_formatter.get_style_defs(prefix_selector)
    return delete_pygments_css_preamble(pygments_css, prefix_selector)


def generate_highlighter_pygments_css_preamble(
    day_style: pygments.style.Style,
    night_style: pygments.style.Style,
) -> str:
    preamble = textwrap.dedent(f"""
        .{PYGMENTS_CLASS}>pre {{
          background: {day_style.background_color};
          color: {day_style.styles[pygments.style.Token]};
          border: solid;
          border-width: thick;
          border-color: {SOLARIZED_LIGHT_BORDER_COLOR};
          padding: 3px 5px;
          line-height: 125%;
          /* Fixes https://github.com/gregorias/anki-code-highlighter/issues/96#issuecomment-3146469831 */
          overflow-x: auto;
        }}
        {NIGHT_MODE_SELECTOR} .{PYGMENTS_CLASS}>pre {{
          background: {night_style.background_color};
          color: {night_style.styles[pygments.style.Token]};
          border-color: {SOLARIZED_DARK_BORDER_COLOR};
        }}
    """).strip()
    return preamble


def generate_highlighter_pygments_css() -> str:
    """Generates the CSS for Pygments highlighting."""
    day_style = pygments.styles.get_style_by_name(DAY_STYLE)
    night_style = pygments.styles.get_style_by_name(NIGHT_STYLE)

    css_parts = [
        generate_highlighter_pygments_css_preamble(day_style, night_style),
        get_pygments_token_css(day_style, DAY_MODE_SELECTOR_STR),
        get_pygments_token_css(night_style, NIGHT_MODE_SELECTOR_STR),
    ]
    return "\n".join(css_parts)


def format_css_sheet(css_sheet: str) -> str:
    """Formats a CSS sheet using Prettier."""
    import subprocess

    try:
        result = subprocess.run(
            ["prettier", "--stdin-filepath", "input.css"],
            input=css_sheet,
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Prettier formatting failed: {e.stderr}.")


def main():
    css_sheet = generate_highlighter_pygments_css()
    print(format_css_sheet(css_sheet), end="")


if __name__ == "__main__":
    main()
