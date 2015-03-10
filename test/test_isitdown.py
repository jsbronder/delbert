import unittest

import base

class IsItDownTester(unittest.TestCase):
    def setUp(self):
        self._plugin = base.load_plugin('isitdown.py', 'IsItDown')
        self._proto = base.TestProto([self._plugin])

    def test_parse(self):
        site = self._plugin.parse_site('http://site.com')
        self.assertEqual(site, 'site.com')

        site = self._plugin.parse_site('https://site.com')
        self.assertEqual(site, 'site.com')

        site = self._plugin.parse_site('http://site.com/images')
        self.assertEqual(site, 'site.com')

        site = self._plugin.parse_site('site.com')
        self.assertEqual(site, 'site.com')

        site = self._plugin.parse_site('site.com/images')
        self.assertEqual(site, 'site.com')

    @base.net_test
    def test_query(self):
        site = self._plugin.parse_site('http://downforeveryoneorjustme.com/')
        up = self._plugin.query(site)
        self.assertTrue(up)

        up = self._plugin.query('sitedoesnotexist.com')
        self.assertFalse(up)

    @base.net_test
    def test_msg(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!isitdown http://google.com/blah')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(
                self._proto.msgs[0][2],
                'google.com is up')

def main():
    unittest.main()

if __name__ == '__main__':
    main()
