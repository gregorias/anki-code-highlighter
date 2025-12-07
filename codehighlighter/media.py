"""This module handles Anki media files."""

import contextlib
import typing
from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path

from anki.media import MediaManager

from .osextra import list_files_with_prefix


class MediaInstaller(ABC):
    @abstractmethod
    def install_media_assets(self) -> None:
        """Installs all add-on's media."""
        pass

    @abstractmethod
    def delete_media_assets(self) -> None:
        """Deletes all add-on's media."""
        pass


class AnkiMediaInstaller(MediaInstaller):
    def __init__(
        self, addon_prefix: str, addon_assets: list[Path], media_manager: MediaManager
    ):
        self.addon_prefix = addon_prefix
        self.addon_assets = addon_assets
        self.media = media_manager

    def install_media_assets(self) -> None:
        install_media_assets(self.addon_assets, self.media)

    def delete_media_assets(self):
        delete_media_assets(self.addon_prefix, self.media)


def anki_media_directory(media: MediaManager) -> Path:
    return Path(media.dir())


def install_media_assets(assets: list[Path], media: MediaManager) -> None:
    for asset in assets:
        media.add_file(str(asset))


def delete_media_assets(asset_prefix: str, media: MediaManager) -> None:
    """Deletes all media assets whose filenames starts with `asset_prefix`"""
    my_assets = list_files_with_prefix(anki_media_directory(media), asset_prefix)
    media.trash_files(my_assets)


@contextlib.contextmanager
def open_media_asset(media: MediaManager, path: Path, mode: str) -> Iterator[typing.IO]:
    """Reads an Anki media asset at the provided path.

    Args:
        path: the relative path to the asset.

    Returns:
        The asset itself.
    """
    with open(anki_media_directory(media) / path, mode) as f:
        yield f
