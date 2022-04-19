# -*- coding: utf-8 -*-
import tempfile
import unittest

from codehighlighter import assets


class FakeAssetManager:

    def __init__(self, local_version: int, plugin_version: int):
        self.local_version = local_version
        self.plugin_version = plugin_version

    def has_newer_version(self) -> bool:
        return self.plugin_version > self.local_version

    def install_assets(self) -> None:
        self.local_version = self.plugin_version

    def delete_assets(self) -> None:
        self.local_version = 0


class AssetsTestCase(unittest.TestCase):

    def test_sync_assets_syncs_on_version_mismatch(self):
        manager = FakeAssetManager(local_version=1, plugin_version=2)
        assets.sync_assets(manager)
        self.assertEqual(manager.local_version, 2)

    def test_sync_assets_passes_if_newer_version_present(self):
        manager = FakeAssetManager(local_version=2, plugin_version=1)
        assets.sync_assets(manager)
        self.assertEqual(manager.local_version, 2)

    def test_read_asset_version_returns_none_on_nonexistant_file(self):
        self.assertEqual(assets.read_asset_version("./foo/bar"), None)

    def test_read_asset_version_returns_version(self):
        with tempfile.NamedTemporaryFile() as version_f:
            version_f.writelines([b'42'])
            version_f.flush()
            self.assertEqual(assets.read_asset_version(version_f.name), 42)

    def test_configure_and_clear_do_nothing(self):
        tmpl = """{{FrontSide}}
                    <hr id=answer>
                    {{Back}}

                    {{#Notes}}
                    <div id=notes>
                    <h4>Notes</h4>
                    {{Notes}}"""
        old_tmpl = tmpl

        def modify_tmpl(modify):
            nonlocal tmpl
            tmpl = modify(tmpl)

        assets.configure_cards(modify_tmpl)
        assets.clear_cards(modify_tmpl)
        self.assertEqual(tmpl, old_tmpl)
