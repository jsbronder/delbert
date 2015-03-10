import unittest

import base

class StartupTester(unittest.TestCase):
    def setUp(self):
        self._startup = base.load_plugin('startup.py', 'Startup')
        self._proto = base.TestProto([self._startup])

    @base.net_test
    def test_query(self):
        m = self._startup.query_startup()
        self.assertTrue(m.startswith('So, basically, it'))

    @base.net_test
    def test_msg(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!startup')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertTrue(self._proto.msgs[0][2].startswith('So, basically, it'))

def main():
    unittest.main()

if __name__ == '__main__':
    main()
