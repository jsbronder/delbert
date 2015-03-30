import unittest

import responses

import base

class ExcusesTester(unittest.TestCase):
    def setUp(self):
        self._plugin = base.load_plugin('excuses.py', 'Excuses')
        self._proto = base.TestProto([self._plugin])

    @base.net_test
    def test_query_real(self):
        m = self._plugin.query_excuse()
        self.assertIsNotNone(m)

    @responses.activate
    def test_query(self):
        base.create_response('http://developerexcuses.com', '<a>dog ate it</a>')

        m = self._plugin.query_excuse()
        self.assertEqual(m, 'dog ate it')

    @responses.activate
    def test_msg(self):
        base.create_response('http://developerexcuses.com', '<a>dog ate it</a>')

        self._proto.privmsg('tester', base.TEST_CHANNEL, '!excuse')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0][2], 'dog ate it')

def main():
    unittest.main()

if __name__ == '__main__':
    main()
