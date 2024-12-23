from typing import NewType

__all__ = [
    'HtmlString',
    'PlainString',
]

HtmlString = NewType('HtmlString', str)

# A plain string that is not supposed to contain any markup.
PlainString = NewType('PlainString', str)
