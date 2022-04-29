# -*- coding: utf-8 -*-
"""This module manages the plugin's assets (JS, CSS files and templates)."""
import os.path
import pathlib
import re
from typing import Callable, List, Optional, Protocol, Union

from anki.collection import Collection
from aqt import mw  # type: ignore


class AssetManager(Protocol):

    def has_newer_version(self) -> bool:
        return False

    def install_assets(self) -> None:
        return None

    def delete_assets(self) -> None:
        return None


class AnkiAssetManager:

    def __init__(self, modify_templates: Callable[[Callable[[str], str]],
                                                  None], col: Collection):
        self.modify_templates = modify_templates
        self.col = col

    def has_newer_version(self) -> bool:
        new_version = read_asset_version(codehighlighter_assets_directory() /
                                         '_ch-asset-version.txt')
        old_version = read_asset_version(
            anki_media_directory(self.col) / '_ch-asset-version.txt')
        if new_version is None:
            return False
        elif old_version is None or new_version > old_version:
            return True
        else:
            return False

    def install_assets(self) -> None:
        install_media_assets(self.col)
        configure_cards(self.modify_templates)

    def delete_assets(self) -> None:
        clear_cards(self.modify_templates)
        delete_media_assets(self.col)


addon_path = os.path.dirname(__file__)


def read_asset_version(asset_version_path: pathlib.Path) -> Optional[int]:
    """Reads the integer representing the asset version from the file."""
    try:
        with open(asset_version_path, 'r') as f:
            return int(f.read())
    except:
        return None


def codehighlighter_assets_directory() -> pathlib.Path:
    return pathlib.Path(addon_path) / 'assets'


def anki_media_directory(col: Collection) -> pathlib.Path:
    return pathlib.Path(col.media.dir())


def list_my_assets(dir: pathlib.Path) -> List[str]:
    return [f for f in os.listdir(dir) if f.startswith("_ch-")]


def install_media_assets(col: Collection) -> None:
    codehighlighter_assets_dir = codehighlighter_assets_directory()
    my_assets = list_my_assets(codehighlighter_assets_dir)
    for asset in my_assets:
        col.media.add_file(str(codehighlighter_assets_dir / asset))


def delete_media_assets(col: Collection) -> None:
    my_assets = list_my_assets(anki_media_directory(col))
    col.media.trash_files(my_assets)


IMPORT_STATEMENTS = (
    '<link rel="stylesheet" href="_ch-pygments-solarized.old.css" class="anki-code-highlighter">\n'
    +
    '<link rel="stylesheet" href="_ch-pygments-solarized.css" class="anki-code-highlighter">\n'
    +
    '<link rel="stylesheet" href="_ch-hljs-solarized.css" class="anki-code-highlighter">\n'
    '<script src="_ch-my-highlight.js" class="anki-code-highlighter"></script>\n'
)


def configure_cards(
        modify_templates: Callable[[Callable[[str], str]], None]) -> None:

    def append_import_statements(tmpl):
        return tmpl + '\n' + IMPORT_STATEMENTS

    modify_templates(append_import_statements)


def clear_cards(
        modify_templates: Callable[[Callable[[str], str]], None]) -> None:

    def delete_import_statements(tmpl):
        return re.sub('^<[^>]*class="anki-code-highlighter"[^>]*>[^\n]*\n',
                      "",
                      tmpl,
                      flags=re.MULTILINE)

    modify_templates(lambda tmpl: delete_import_statements(tmpl).strip())


def sync_assets(asset_manager: AssetManager) -> None:
    """Checks if assets need updating and updates them."""
    if not asset_manager.has_newer_version():
        return None
    asset_manager.delete_assets()
    asset_manager.install_assets()
