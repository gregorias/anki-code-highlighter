# Media refers to static JS and CSS files.
from codehighlighter.media import MediaInstaller

__all__ = ["FakeMediaInstaller"]


class FakeMediaInstaller(MediaInstaller):
    """A fake media installer for testing purposes."""

    def __init__(
        self, initial_files: list[str] = [], addon_assets: list[str] = []
    ) -> None:
        self.files = initial_files.copy()
        self.addon_assets = addon_assets.copy()

    def install_media_assets(self) -> None:
        self.files = list(set(self.files + self.addon_assets))

    def delete_media_assets(self):
        self.files = [f for f in self.files if not f.startswith("_ch")]
