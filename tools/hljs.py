"""A suite of tools for working with highlight.js."""

import contextlib
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import textwrap
import typing


@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)


HLJS_VERSION = '11.8.0'
HLJS_REPO = 'https://github.com/highlightjs/highlight.js'


def delete_old_hljs_scripts() -> None:
    """Deletes all JS files associated with HLJS in assets/."""
    for f in os.listdir('assets'):
        if f.startswith('_ch-hljs-lang-'):
            os.remove(f'assets/{f}')
    os.remove('assets/_ch-highlight.js')


class HLJSBuild(typing.NamedTuple):
    hljs_file: pathlib.Path
    hljs_min_file: pathlib.Path


def build_hljs() -> HLJSBuild:
    """Builds highlight.js in the current directory."""
    hljs_dir = 'highlight.js'
    subprocess.run(['git', 'clone', HLJS_REPO])
    with pushd(hljs_dir):
        subprocess.run(['git', 'checkout', HLJS_VERSION])
        subprocess.run(['npm', 'install'])
        subprocess.run(['node', 'tools/build.js', '-t', 'browser'])

        hljs_file = 'build/highlight.js'
    return HLJSBuild(
        hljs_file=pathlib.Path(f'{hljs_dir}/build/highlight.js'),
        hljs_min_file=pathlib.Path(f'{hljs_dir}/build/highlight.min.js'))


class Language(typing.NamedTuple):
    name: str
    alias: str


def extract_languages_from_highlight_js(
        highlight_js_path: pathlib.Path) -> typing.Iterator[Language]:
    """Extracts languages supported by highlight.js."""
    extraction = subprocess.run([
        'node', 'tools/extract-hljs-languages.js',
        highlight_js_path.resolve()
    ],
                                capture_output=True,
                                check=True)
    for line in extraction.stdout.decode('utf-8').splitlines():
        language_json = json.loads(line)
        yield Language(name=language_json['name'],
                       alias=language_json['alias'])


def generate_hljs_languages_python_list(languages: typing.Iterable[Language],
                                        out: typing.TextIO):
    """Generates a Python module containing a list of all supported languages."""
    out.write(
        textwrap.dedent(f"""\
      \"""A list of all supported languages in highlight.js.

      This file is automatically generated by tools.
      \"""
      import typing


      class Language(typing.NamedTuple):
          \"""A language supported by highlight.js.\"""
          name: str
          alias: str


      languages: typing.List[Language] = [
    """))

    for language in languages:
        out.write(f'    {repr(language)},\n')
    out.write(']')


def update_hljs_main():
    """Installs HLJS_VERSION of highlight.js."""
    with tempfile.TemporaryDirectory() as d:
        with pushd(d):
            hljs_build = build_hljs()
        hljs_build = HLJSBuild(
            hljs_file=pathlib.Path(d) / hljs_build.hljs_file,
            hljs_min_file=pathlib.Path(d) / hljs_build.hljs_min_file)
        delete_old_hljs_scripts()
        shutil.copy(hljs_build.hljs_min_file, 'assets/_ch-highlight.js')

        with open('codehighlighter/hljslangs.py', 'w') as hljslangs_py:
            generate_hljs_languages_python_list(
                extract_languages_from_highlight_js(hljs_build.hljs_file),
                hljslangs_py)


if __name__ == '__main__':
    update_hljs_main()
