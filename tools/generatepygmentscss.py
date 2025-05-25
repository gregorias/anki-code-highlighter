"""Generates the CSS for pygments highlighting."""

import colorsys
import textwrap

import cssutils  # type: ignore
import webcolors  # type: ignore

import pygments
import pygments.formatters
import pygments.formatters.html
import pygments.style
import pygments.styles

DAY_STYLE = 'solarized-light'
NIGHT_STYLE = 'solarized-dark'
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


def brighten_color(hex: str, factor: float) -> str:
    rp = webcolors.hex_to_rgb(hex)
    h, l, s = colorsys.rgb_to_hls(rp.red / 255, rp.green / 255, rp.blue / 255)
    new_rgb_triplet = tuple(
        int(i * 255) for i in colorsys.hls_to_rgb(h, l * factor, s))
    return webcolors.rgb_to_hex(
        webcolors.normalize_integer_triplet(new_rgb_triplet))


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
          border-color: {brighten_color(day_style.background_color,
                                        factor=0.45)};
          padding: 3px 5px;
          line-height: 125%;
        }}
        .{NIGHT_MODE_CLASS} .{PYGMENTS_CLASS}>pre {{
          background: {night_style.background_color};
          color: {night_style.styles[pygments.style.Token]};
          border-color: {brighten_color(night_style.background_color,
                                        factor=1.5)};
        }}
    """).strip()
    return cssutils.parseString(preamble)


def generate_highlighter_pygments_css() -> cssutils.css.CSSStyleSheet:
    """Generates the CSS for pygments highlighting."""
    day_style = pygments.styles.get_style_by_name(DAY_STYLE)
    night_style = pygments.styles.get_style_by_name(NIGHT_STYLE)

    css_preamble = generate_highlighter_pygments_css_preamble(
        day_style, night_style)
    css = css_preamble
    css.cssRules.extend(
        get_pygments_css(day_style, DAY_MODE_SELECTOR).cssRules)
    css.cssRules.extend(
        get_pygments_css(night_style, NIGHT_MODE_SELECTOR).cssRules)
    return css_preamble


def main():
    print(generate_highlighter_pygments_css().cssText.decode('utf8'))


if __name__ == '__main__':
    main()
