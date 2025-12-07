import tempfile
import unittest
from pathlib import Path
from textwrap import dedent

from codehighlighter import assets
from codehighlighter.assets import AnkiAssetManager

from .media import FakeMediaInstaller
from .model import FakeModelModifier


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
        initial_template = "{{FrontSide}}\n"
        initial_css = "body { background-color: white; }"
        initial_media_files = ["foo.png"]
        addon_assets = ["_ch-pygments-solarized.css"]

        model_modifier = FakeModelModifier([initial_template], [initial_css])
        media_installer = FakeMediaInstaller(
            initial_media_files, addon_assets=addon_assets
        )

        manager = AnkiAssetManager(
            model_modifier,
            media_installer,
            css_assets=["_ch-pygments-solarized.css"],
            guard="ACH add-on",
            class_name="anki-code-highlighter",
        )

        manager.install_assets()

        self.assertEqual(model_modifier.templates[0], initial_template)
        self.assertEqual(
            model_modifier.csss[0],
            "/* ACH add-on BEGIN */\n"
            + '@import "_ch-pygments-solarized.css";\n'
            + "/* ACH add-on END */\n"
            + "\n"
            + initial_css,
        )
        self.assertSetEqual(
            set(media_installer.files), set(initial_media_files + addon_assets)
        )

    def test_install_and_delete_do_nothing(self):
        initial_template = "{{FrontSide}}\n"
        initial_css = "body { background-color: white; }"
        initial_media_files = ["foo.png"]
        addon_assets = ["_ch-pygments-solarized.css"]

        model_modifier = FakeModelModifier([initial_template], [initial_css])
        media_installer = FakeMediaInstaller(
            initial_media_files, addon_assets=addon_assets
        )

        manager = AnkiAssetManager(
            model_modifier,
            media_installer,
            css_assets=["_ch-pygments-solarized.css"],
            guard="ACH add-on",
            class_name="anki-code-highlighter",
        )

        manager.install_assets()
        manager.delete_assets()

        self.assertEqual(model_modifier.templates[0], initial_template)
        self.assertEqual(model_modifier.csss[0], initial_css)
        self.assertListEqual(media_installer.files, initial_media_files)

    def test_delete_assets(self):
        model_modifier = FakeModelModifier(
            [
                dedent(
                    """\
           {{Front}}

           <!-- ACH add-on BEGIN -->
           <link rel="stylesheet" href="_ch-pygments-solarized.css" class="anki-code-highlighter">
           <script src="j.js" class="plugin"></script>
           <!-- ACH add-on END -->
           """
                )
            ],
            [
                "/* ACH add-on BEGIN */\n"
                + 'import "_ch-foo.css"\n'
                + "/* ACH add-on END */\n"
                + "\n"
                + "body {}\n"
            ],
        )
        media_installer = FakeMediaInstaller(["_ch-foo.css", "foo.png"])
        manager = AnkiAssetManager(
            model_modifier,
            media_installer,
            css_assets=["_ch-foo.css"],
            guard="ACH add-on",
            class_name="ach",
        )

        manager.delete_assets()

        self.assertEqual(model_modifier.templates[0], "{{Front}}\n")
        self.assertEqual(model_modifier.csss[0], "body {}\n")
        self.assertListEqual(media_installer.files, ["foo.png"])
