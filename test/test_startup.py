import unittest

import responses

import base

class StartupTester(unittest.TestCase):
    def setUp(self):
        self._startup = base.load_plugin('startup.py', 'Startup')
        self._proto = base.TestProto([self._startup])

    @base.net_test
    def test_query_real(self):
        m = self._startup.query_startup()
        self.assertTrue(m.startswith('So, basically, it'))

    @responses.activate
    def test_query(self):
        base.create_response('http://itsthisforthat.com/.*', 'a test')

        m = self._startup.query_startup()
        self.assertEqual(m, 'A test')

    @responses.activate
    def test_msg(self):
        base.create_response('http://itsthisforthat.com/.*', 'a test')

        self._proto.privmsg('tester', base.TEST_CHANNEL, '!startup')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0][2], 'A test')

def main():
    unittest.main()

if __name__ == '__main__':
    main()
