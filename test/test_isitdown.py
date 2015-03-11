import unittest

import responses

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
    def test_query_real(self):
        up = self._plugin.query('http://google.com')
        self.assertTrue(up)

        up = self._plugin.query('http://aceoiuhcaeoiacheoichajefoi.com')
        self.assertFalse(up)

    @responses.activate
    def test_query(self):
        base.create_response('http://downforeveryoneorjustme.com/blah', '')
        base.create_response('http://downforeveryoneorjustme.com/halb', 'not just you!')

        up = self._plugin.query('blah')
        self.assertTrue(up)

        up = self._plugin.query('halb')
        self.assertFalse(up)

    @responses.activate
    def test_msg(self):
        base.create_response('http://downforeveryoneorjustme.com/blah.com', '')

        self._proto.privmsg('tester', base.TEST_CHANNEL, '!isitdown http://blah.com')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(
                self._proto.msgs[0][2],
                'blah.com is up')

def main():
    unittest.main()

if __name__ == '__main__':
    main()
