"""Generates the CSS for pygments highlighting."""

import textwrap

import cssutils  # type: ignore

import pygments
import pygments.formatters
import pygments.formatters.html
import pygments.style
import pygments.styles

DAY_STYLE = 'solarized-light'
NIGHT_STYLE = 'solarized-dark'
SOLARIZED_LIGHT_BORDER_COLOR = '#cdbc84'
SOLARIZED_DARK_BORDER_COLOR = '#052831'
PYGMENTS_CLASS = 'pygments'
NIGHT_MODE_CLASS = 'night_mode'
DAY_MODE_SELECTOR = cssutils.css.Selector(f'.{PYGMENTS_CLASS}')
NIGHT_MODE_SELECTOR = cssutils.css.Selector(
    f'.{NIGHT_MODE_CLASS} .{PYGMENTS_CLASS}')


def delete_pygments_css_preamble(pygments_css_rules: cssutils.css.CSSRuleList,
                                 selector: cssutils.css.Selector):
    """Deletes code block styles.

    This plugin defines its own style for code blocks, so we don't want to keep
    the default Pygments styles.
    """
    while PYGMENTS_CLASS not in pygments_css_rules[0].selectorText:
        pygments_css_rules.pop(0)

    for rule in pygments_css_rules:
        if rule.selectorText == selector.selectorText:
            pygments_css_rules.remove(rule)
            break


def get_pygments_css(
        style: pygments.style.Style,
        selector: cssutils.css.Selector) -> cssutils.css.CSSStyleSheet:
    """Gets the CSS of a particular Pygments style without the preamble."""
    # In the context of this plugin, only the HTML formatter is used.
    html_formatter: pygments.formatters.html.HtmlFormatter = (
        pygments.formatters.get_formatter_by_name('html', style=style))
    pygments_css = cssutils.parseString(
        html_formatter.get_style_defs(selector.selectorText))
    delete_pygments_css_preamble(pygments_css.cssRules, selector)
    return pygments_css


def generate_highlighter_pygments_css_preamble(
    day_style: pygments.style.Style,
    night_style: pygments.style.Style,
) -> cssutils.css.CSSStyleSheet:
    preamble = textwrap.dedent(f"""
        .{PYGMENTS_CLASS}>pre {{
          background: {day_style.background_color};
          color: {day_style.styles[pygments.style.Token]};
          border: solid;
          border-width: thick;
          border-color: {SOLARIZED_LIGHT_BORDER_COLOR};
          padding: 3px 5px;
          line-height: 125%;
        }}
        .{NIGHT_MODE_CLASS} .{PYGMENTS_CLASS}>pre {{
          background: {night_style.background_color};
          color: {night_style.styles[pygments.style.Token]};
          border-color: {SOLARIZED_DARK_BORDER_COLOR};
        }}
    """).strip()
    return cssutils.parseString(preamble)


def generate_highlighter_pygments_css() -> cssutils.css.CSSStyleSheet:
    """Generates the CSS for pygments highlighting."""
    day_style = pygments.styles.get_style_by_name(DAY_STYLE)
    night_style = pygments.styles.get_style_by_name(NIGHT_STYLE)

    css = generate_highlighter_pygments_css_preamble(day_style, night_style)
    css.cssRules.extend(
        get_pygments_css(day_style, DAY_MODE_SELECTOR).cssRules)
    css.cssRules.extend(
        get_pygments_css(night_style, NIGHT_MODE_SELECTOR).cssRules)
    return css


def format_css_sheet(css_sheet: str) -> str:
    """Formats a CSS sheet using Prettier."""
    import subprocess

    try:
        result = subprocess.run(["prettier", "--stdin-filepath", "input.css"],
                                input=css_sheet,
                                text=True,
                                capture_output=True,
                                check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Prettier formatting failed: {e.stderr}.")


def main():
    css_sheet = (generate_highlighter_pygments_css().cssText.decode('utf8'))
    print(format_css_sheet(css_sheet))


if __name__ == '__main__':
    main()
