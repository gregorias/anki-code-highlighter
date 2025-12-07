import tempfile
import unittest
from pathlib import Path
from textwrap import dedent

from codehighlighter import assets
from codehighlighter.assets import (
    AnkiAssetManager,
    append_import_statements,
    delete_import_statements,
)

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

    def test_append_and_clear_import_statements_do_nothing(self):
        tmpl = """{{FrontSide}}
                    <hr id=answer>
                    {{Back}}

                    {{#Notes}}
                    <div id=notes>
                    <h4>Notes</h4>
                    {{Notes}}"""

        GUARD = "PLUGIN (Addon 123)"
        CLASS_NAME = "anki-ch"

        new_tmpl = append_import_statements(
            ["c.css"], ["console.log('foo')"], GUARD, CLASS_NAME, tmpl
        )
        self.assertEqual(delete_import_statements(GUARD, new_tmpl), tmpl + "\n")

    def test_append_import_statements_adds_them_with_a_gap(self):
        self.assertEqual(
            append_import_statements(
                ["c.css"],
                ["console.log('foo')"],
                "Anki Code Highlighter (Addon 112228974)",
                "plugin",
                "{{Cloze}}",
            ),
            dedent(
                """\
            {{Cloze}}

            <!-- Anki Code Highlighter (Addon 112228974) BEGIN -->
            <link rel="stylesheet" href="c.css" class="plugin">
            <script class="plugin">console.log('foo')</script>
            <!-- Anki Code Highlighter (Addon 112228974) END -->
            """
            ),
        )

    def test_append_import_statements_adds_them_with_a_gap_and_minds_a_newline_in_template(
        self,
    ):
        self.assertEqual(
            append_import_statements(
                ["c.css"],
                ["console.log('foo')"],
                "Anki Code Highlighter (Addon 112228974)",
                "plugin",
                "{{Cloze}}\n",
            ),
            dedent(
                """\
            {{Cloze}}

            <!-- Anki Code Highlighter (Addon 112228974) BEGIN -->
            <link rel="stylesheet" href="c.css" class="plugin">
            <script class="plugin">console.log('foo')</script>
            <!-- Anki Code Highlighter (Addon 112228974) END -->
            """
            ),
        )

    def test_delete_import_statements_deletes_new_style_imports(self):
        TMPL = dedent(
            """\
            {{Cloze}}

            <!-- Anki Code Highlighter (Addon 112228974) BEGIN -->
            <link rel="stylesheet" href="c.css" class="plugin">
            <script src="j.js" class="plugin"></script>
            <!-- Anki Code Highlighter (Addon 112228974) END -->
            """
        )
        self.assertEqual(
            delete_import_statements("Anki Code Highlighter (Addon 112228974)", TMPL),
            "{{Cloze}}\n",
        )


class AssetsManagerTestCase(unittest.TestCase):

    def test_delete_assets(self):
        model_modifier = FakeModelModifier(
            [
                dedent(
                    """\
           {{Front}}

           <!-- ACH add-on BEGIN -->
           <link rel="stylesheet" href="_ch-pygments-solarized.css" class="anki-code-highlighter">
           <!-- ACH add-on END -->
           """
                )
            ]
        )
        media_installer = FakeMediaInstaller(["_ch-foo.css", "foo.png"])
        manager = AnkiAssetManager(
            model_modifier,
            media_installer,
            css_assets=["_ch-foo.css"],
            script_elements=[],
            guard="ACH add-on",
            class_name="ach",
        )

        manager.delete_assets()

        self.assertEqual(
            model_modifier.templates[0],
            dedent(
                """\
               {{Front}}
               """
            ),
        )
        self.assertListEqual(media_installer.files, ["foo.png"])
