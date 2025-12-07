"""This module manages the plugin's assets (JS, CSS files, and templates).

The module is plugin agnostic: it contains generic mechanisms for updating
relevant assets.
"""

import contextlib
import os.path
import pathlib
import typing
from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from anki.media import MediaManager

from .guard import append_guarded_snippet, delete_guarded_snippet, guard_html_comments
from .media import (
    MediaInstaller,
    anki_media_directory,
    open_media_asset,
)
from .model import ModelModifier
from .osextra import list_files_with_prefix
from .serialization import Serializer

# This list contains the intended public API of this module.
__all__ = [
    "AssetManager",
    "AnkiAssetManager",
    "has_newer_version",
    "sync_assets",
    "append_import_statements",
    "delete_import_statements",
]


class AssetManager(Protocol):
    """An object that can install and delete an add-on’s assets."""

    def install_assets(self) -> None:
        return None

    def delete_assets(self) -> None:
        return None


def has_newer_version(media: MediaManager, version_asset: str) -> bool:
    """
    Returns whether the plugin has newer asset version.

    :param media Anki's media manager
    :param version_asset The version asset filename.
    :rtype Whether the plugin has newer asset version.
    """
    new_version = read_asset_version(assets_directory() / version_asset)
    old_version = read_asset_version(anki_media_directory(media) / version_asset)
    if new_version is None:
        return False
    elif old_version is None or new_version > old_version:
        return True
    else:
        return False


def read_asset_version(asset_version_path: pathlib.Path) -> int | None:
    """Reads the integer representing the asset version from the file."""
    try:
        with open(asset_version_path, "r") as f:
            return int(f.read())
    except Exception:
        return None


class AnkiAssetManager:
    # We used to load JS files in script elements but that was causing a
    # flicker (https://github.com/gregorias/anki-code-highlighter/issues/94).

    def __init__(
        self,
        model_modifier: ModelModifier,
        media_installer: MediaInstaller,
        css_assets: list[str],
        script_elements: list[str],
        guard: str,
        class_name: str,
    ):
        """
        :param model_modifier
        :param media_installer
        :param css_assets All CSS files used by this plugin.
        :param script_elements JS scripts to run.
        :param guard A guard string used for HTML comments wrapping the imports.
        :param class_name The unique HTML class name that this manager can use
            to identify its HTML elements.
        """
        self.model_modifier = model_modifier
        self.media_installer = media_installer
        self.css_assets = css_assets
        self.script_elements = script_elements
        self.guard = guard
        self.class_name = class_name

    def install_assets(self) -> None:
        self.media_installer.install_media_assets()
        self.model_modifier.modify_templates(
            lambda tmpl: append_import_statements(
                css_assets=self.css_assets,
                script_elements=self.script_elements,
                guard=self.guard,
                class_name=self.class_name,
                tmpl=tmpl,
            )
        )

    def delete_assets(self) -> None:
        self.model_modifier.modify_templates(
            lambda tmpl: delete_import_statements(guard=self.guard, tmpl=tmpl)
        )
        self.media_installer.delete_media_assets()


addon_path = os.path.dirname(__file__)


def assets_directory() -> pathlib.Path:
    """Returns the path to the plugin’s assets directory.

    The plugin’s asset directory is the static directory with the assets
    bundled with this plugin.

    Returns:
        The asset path.
    """
    return pathlib.Path(addon_path) / "assets"


def append_import_statements(
    css_assets: list[str],
    script_elements: list[str],
    guard: str,
    class_name: str,
    tmpl: str,
) -> str:
    """
    Appends import statements to a card template.

    :param css_assets
    :param script_elements
    :param guard A guard string used for HTML comments wrapping the imports.
    :param class_name A class name that identifies this plugin.
    :param tmpl
    :rtype A template with added import statements.
    """
    IMPORT_STATEMENTS = "".join(
        [
            f'<link rel="stylesheet" href="{css_asset}" class="{class_name}">\n'
            for css_asset in css_assets
        ]
        + [
            f'<script class="{class_name}">{script}</script>\n'
            for script in script_elements
        ]
    )

    return append_guarded_snippet(
        tmpl, IMPORT_STATEMENTS, guards=guard_html_comments(guard)
    )


def delete_import_statements(guard: str, tmpl: str) -> str:
    """
    Deletes import statements from a card template.

    :param guard A guard string used for HTML comments wrapping the imports.
    :param tmpl
    :rtype template with deleted import statements.
    """
    return delete_guarded_snippet(tmpl, guard_html_comments(guard))


def sync_assets(
    has_newer_version: Callable[[], bool], asset_manager: AssetManager
) -> None:
    """Checks if assets need updating and updates them."""
    if has_newer_version():
        asset_manager.delete_assets()
        asset_manager.install_assets()


def get_addon_assets(asset_prefix: str) -> list[Path]:
    assets_dir = assets_directory()
    my_assets = list_files_with_prefix(assets_dir, asset_prefix)
    return [assets_dir / a for a in my_assets]


T = typing.TypeVar("T")


class State(typing.Generic[T]):
    """Mutable state object."""

    def __init__(self, initial: T):
        self.value = initial

    def get(self) -> T:
        return self.value

    def put(self, val: T) -> None:
        self.value = val


@contextlib.contextmanager
def AnkiAssetStateManager(
    media: MediaManager, path: pathlib.Path, serializer: Serializer[T], default: T
) -> typing.Generator[State[T], None, None]:
    try:
        with open_media_asset(media, path, "r") as f:
            content = serializer.loads(f.read()) or default
    except Exception:
        content = default

    state: State[T] = State(content)
    try:
        yield state
    finally:
        with open_media_asset(media, path, "w") as f:
            serialized_content = serializer.dumps(state.get())
            f.write(serialized_content)
