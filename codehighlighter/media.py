"""This module handles Anki media files."""

import contextlib
import pathlib
import typing
from collections.abc import Iterator

from anki.media import MediaManager

from .osextra import list_files_with_prefix


def anki_media_directory(media: MediaManager) -> pathlib.Path:
    return pathlib.Path(media.dir())


def delete_media_assets(asset_prefix: str, media: MediaManager) -> None:
    """Deletes all media assets whose filenames starts with `asset_prefix`"""
    my_assets = list_files_with_prefix(anki_media_directory(media), asset_prefix)
    media.trash_files(my_assets)


@contextlib.contextmanager
def open_media_asset(
    media: MediaManager, path: pathlib.Path, mode: str
) -> Iterator[typing.IO]:
    """Reads an Anki media asset at the provided path.

    Args:
        path: the relative path to the asset.

    Returns:
        The asset itself.
    """
    with open(anki_media_directory(media) / path, mode) as f:
        yield f
