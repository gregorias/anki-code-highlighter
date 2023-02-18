"""Extra functionality specific to highlight.js."""
from typing import List

__all__ = ['get_available_languages']


def get_available_languages(lang_files: List[str]) -> List[str]:
    """
    Gets a list of available HLJS languages from a list of media files.

    :param lang_files List[str]
    :rtype List[str]
    """
    LANG_PREFIX = '_ch-hljs-lang-'
    LANG_SUFFIX = '.min.js'
    return [
        f.removeprefix(LANG_PREFIX).removesuffix(LANG_SUFFIX)
        for f in lang_files
        if f.startswith(LANG_PREFIX) and f.endswith(LANG_SUFFIX)
    ] + [
        "html",
        "xhtml",
        "rss",
        "atom",
        "xjb",
        "xsd",
        "xsl",
        "plist",
        "wsf",
        "svg",
    ]  # These are handled by xml.min.js.
