"""Useful & informant utilities for working with Pygments."""
import re

# cssutils doesn't have type annotations.
import cssutils  # type: ignore

import pygments
import pygments.formatter
import pygments.formatters
import pygments.style
import pygments.styles

solarized_light = pygments.styles.get_style_by_name('solarized-light')
solarized_dark = pygments.styles.get_style_by_name('solarized-dark')


def html_formatter_cls(s):
    return pygments.formatters.get_formatter_by_name('html', style=s)


def get_colors_from_stylesheet(
        stylesheet: cssutils.css.CSSStyleSheet) -> set[str]:
    colors: set[str] = set()
    for rule in stylesheet.cssRules:
        if not isinstance(rule, cssutils.css.CSSStyleRule):
            continue
        c = rule.style.color
        bc = rule.style.backgroundColor
        if c:
            colors.add(c)
        if bc:
            colors.add(bc)
    return colors


def get_stylesheet_from_formatter(
        formatter: pygments.formatter.Formatter) -> cssutils.css.CSSStyleSheet:
    return cssutils.parseString(formatter.get_style_defs())


def create_color_to_variable_map(
        name: str, pstyle: pygments.style.Style) -> dict[str, str]:
    """Assigns each color in a style a unique variable name.

    Returns:
        A dict from a color (e.g., "#123456") to a variable name (e.g.,
        '--pygments-solarized-light-color04').
    """
    stylesheet_str = html_formatter_cls(pstyle).get_style_defs()
    colors = get_colors_from_stylesheet(cssutils.parseString(stylesheet_str))
    colors.add(pstyle.background_color)  # type: ignore
    colors.add(pstyle.highlight_color)  # type: ignore
    # Excluding lineos colors, because I don't use them.

    colors_to_variable = dict()
    for i, color in enumerate(colors):
        colors_to_variable[color] = f'--pygments-{name}-color{i:02}'
    return colors_to_variable


def filter_lines(pred, input: str) -> str:
    return ''.join([line + '\n' for line in filter(pred, input.splitlines())])


def replace_inlined_color_with_variable(color: str, variable: str,
                                        sheet: str) -> str:
    # Not using CSSOM, because cssutils doesn't support custom properties
    # (https://github.com/jaraco/cssutils/issues/14).
    m = re.match(r'#(\d)(\d)(\d)', color)
    if m:
        color6 = f'#{m.group(1)}{m.group(1)}{m.group(2)}{m.group(2)}{m.group(3)}{m.group(3)}'
        sheet = re.sub(color6, f'var({variable})', sheet)
    sheet = re.sub(color, f'var({variable})', sheet)
    return sheet


def create_pretty_pygments_style() -> str:
    """Creates a pretty pygments-based solarized style for Anki."""
    sl_cvs = create_color_to_variable_map('solarized-light',
                                          solarized_light)  # type: ignore
    sd_cvs = create_color_to_variable_map('solarized-dark',
                                          solarized_dark)  # type: ignore

    root_rule = ':root {\n'
    for c, v in sl_cvs.items():
        root_rule += f'  {v}: {c};\n'
    for c, v in sd_cvs.items():
        root_rule += f'  {v}: {c};\n'
    root_rule += '}\n'

    light_stylesheet: str = html_formatter_cls(solarized_light).get_style_defs(
        '.highlight')
    for c, v in sl_cvs.items():
        light_stylesheet = replace_inlined_color_with_variable(
            c, v, light_stylesheet)
    dark_stylesheet: str = html_formatter_cls(solarized_dark).get_style_defs(
        '.night_mode .highlight')
    for c, v in sd_cvs.items():
        dark_stylesheet = replace_inlined_color_with_variable(
            c, v, dark_stylesheet)
    return root_rule + light_stylesheet + dark_stylesheet


def main():
    print(create_pretty_pygments_style())


if __name__ == "__main__":
    main()
