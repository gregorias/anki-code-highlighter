import tempfile
import unittest
from pathlib import Path

from codehighlighter import assets
from codehighlighter.assets import AnkiAssetManager

from .media import FakeMediaInstaller


class FakeAssetManager:

    def __init__(self, local_version: int, plugin_version: int):
        self.local_version = local_version
        self.plugin_version = plugin_version

    def install_assets(self) -> None:
        self.local_version = self.plugin_version

    def delete_assets(self) -> None:
        self.local_version = 0


class AssetsTestCase(unittest.TestCase):

    def test_sync_assets_syncs_on_version_mismatch(self):
        manager = FakeAssetManager(local_version=1, plugin_version=2)
        assets.sync_assets(lambda: True, manager)
        self.assertEqual(manager.local_version, 2)

    def test_sync_assets_passes_if_newer_version_present(self):
        manager = FakeAssetManager(local_version=2, plugin_version=1)
        assets.sync_assets(lambda: False, manager)
        self.assertEqual(manager.local_version, 2)

    def test_read_asset_version_returns_none_on_nonexistant_file(self):
        self.assertEqual(assets.read_asset_version(Path("./foo/bar")), None)

    def test_read_asset_version_returns_version(self):
        with tempfile.NamedTemporaryFile() as version_f:
            version_f.writelines([b"42"])
            version_f.flush()
            self.assertEqual(assets.read_asset_version(Path(version_f.name)), 42)


class AssetsManagerTestCase(unittest.TestCase):
    def test_install_updates_css_and_media(self):
        initial_media_files = ["foo.png"]
        addon_assets = ["_gch-pygments-solarized.css"]

        media_installer = FakeMediaInstaller(
            initial_media_files, addon_assets=addon_assets
        )

        manager = AnkiAssetManager(
            media_installer,
            css_assets=["_gch-pygments-solarized.css"],
            class_name="anki-code-highlighter",
        )

        manager.install_assets()

        self.assertSetEqual(
            set(media_installer.files), set(initial_media_files + addon_assets)
        )

    def test_install_and_delete_do_nothing(self):
        initial_media_files = ["foo.png"]
        addon_assets = ["_gch-pygments-solarized.css"]

        media_installer = FakeMediaInstaller(
            initial_media_files, addon_assets=addon_assets
        )

        manager = AnkiAssetManager(
            media_installer,
            css_assets=["_gch-pygments-solarized.css"],
            class_name="anki-code-highlighter",
        )

        manager.install_assets()
        manager.delete_assets()

        self.assertListEqual(media_installer.files, initial_media_files)

    def test_delete_assets(self):
        media_installer = FakeMediaInstaller(["_gch-foo.css", "foo.png"])
        manager = AnkiAssetManager(
            media_installer,
            css_assets=["_gch-foo.css"],
            class_name="ach",
        )

        manager.delete_assets()

        self.assertListEqual(media_installer.files, ["foo.png"])
