import unittest

import bs4

from codehighlighter.ankieditorextra import extract_field_from_web_editor, transform_elements_with_id


class AnkiEditorExtraTestCase(unittest.TestCase):

    def test_find_id_elements_and_replace(self):
        field = "<div>Lorem Ipsum</div><div id='foobar123'>code</div>"

        def replace(html: str) -> bs4.Tag:
            soup = bs4.BeautifulSoup()
            code_tag = soup.new_tag('code')
            code_tag.append(html)
            soup.append(code_tag)
            return soup

        expected = "<div>Lorem Ipsum</div><code>code</code>"
        self.assertEqual(
            transform_elements_with_id(field, 'foobar123', replace), expected)

    def test_extract_field_from_web_editor_extracts_field_0(self):
        self.assertEqual(
            extract_field_from_web_editor(
                '<link id="rootStyle" rel="stylesheet" href="./_anki/css/editable.css"><style id="userBase"></style><anki-editable contenteditable="true" class="svelte-18uwveo" style="--editor-shrink-max-width:250px; --editor-shrink-max-height:125px;"><span id="2208">asdf</span></anki-editable>'
            ), '<span id="2208">asdf</span>')

    def test_extract_field_from_web_editor_extracts_field_1(self):
        self.assertEqual(
            extract_field_from_web_editor('''
                <link id="rootStyle" rel="stylesheet" href="./_anki/css/editable.css">
                <style id="userBase"></style>
                <anki-editable contenteditable="true" class="svelte-18uwveo" style="--editor-shrink-max-width:250px; --editor-shrink-max-height:125px;">
                    <span id="2208">asdf</span>
                    Lorem Ipsum
                </anki-editable>'''), '''
                    <span id="2208">asdf</span>
                    Lorem Ipsum
                ''')
