import unittest

import bs4

from codehighlighter.ankieditorextra import transform_elements_with_id


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
