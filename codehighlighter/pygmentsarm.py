# Copied from https://github.com/heia-fr/pygments-arm.
# Added to the repo, because ARM is popular and yet somehow missing from
# Pygments.
# Modified sligthly to provide consistent documentation and fix typos.
"""The Pygments lexer for ARM."""

from pygments.lexer import RegexLexer, include
from pygments.token import Comment, Name, Number, Punctuation, String, Text, Whitespace

__all__ = ["ArmLexer"]


class ArmLexer(RegexLexer):
    name = "ARM"
    aliases = ["arm"]
    filenames = ["*.S"]

    string = r'"(\\"|[^"])*"'
    char = r"[\w$.@-]"
    identifier = r"(?:[a-zA-Z$_]" + char + "*|\\." + char + "+)"
    number = r"(?:0[xX][a-zA-Z0-9]+|\d+)"

    tokens = {
        "root": [
            include("whitespace"),
            (identifier + ":", Name.Label),
            (number + ":", Name.Label),
            (r"\." + identifier, Name.Attribute, "directive-args"),
            (identifier, Name.Function, "instruction-args"),
            (r"[\r\n]+", Text),
        ],
        "directive-args": [
            (identifier, Name.Constant),
            (string, String),
            (number, Number.Integer),
            (r"[\r\n]+", Text, "#pop"),
            include("punctuation"),
            include("whitespace"),
        ],
        "instruction-args": [
            (identifier, Name.Constant),
            (number, Number.Integer),
            # Registers
            (r"[rR]\d+", Name.Variable),
            (r"'(.|\\')'?", String.Char),
            (r"[\r\n]+", Text, "#pop"),
            include("punctuation"),
            include("whitespace"),
        ],
        "whitespace": [
            (r"\s+", Whitespace),
            (r"//[\w\W]*?(?=\n)", Comment.Single),
            (r"/[*][\w\W]*?[*]/", Comment.Multiline),
            (r"[;@].*?(?=\n)", Comment.Single),
        ],
        "punctuation": [(r"[-*,.()\[\]!:{}^=#\+\\]+", Punctuation)],
        "eol": [(r"[\r\n]+", Text)],
    }
