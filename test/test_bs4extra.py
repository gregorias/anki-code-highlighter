import codehighlighter.bs4extra as bs4extra

import unittest


class Bs4ExtraTestCase(unittest.TestCase):

    def test_is_html(self):
        self.assertTrue(bs4extra.is_html('<div>foo</div>'))
        self.assertTrue(bs4extra.is_html('foo<br/>bar'))
        self.assertTrue(bs4extra.is_html('foo<br>bar'))
        self.assertTrue(bs4extra.is_html('foo &lt; bar'))

        self.assertFalse(bs4extra.is_html('5 < 3;'))
        self.assertFalse(bs4extra.is_html('foo'))
        self.assertFalse(bs4extra.is_html('return &foo;'))
