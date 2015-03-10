import unittest

import base

class UDTester(unittest.TestCase):
    def setUp(self):
        self._plugin = base.load_plugin('urban_dictionary.py', 'UrbanDictionary')
        self._proto = base.TestProto([self._plugin])

    @base.net_test
    def test_query(self):
        m = self._plugin.query('test')
        self.assertEqual('A process for testing things', m)

    @base.net_test
    def test_msg(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!ud test')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(
            self._proto.msgs[0][2],
            'test:  A process for testing things')

    @base.net_test
    def test_compound_msg(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!ud compound message')
        self.assertEqual(1, len(self._proto.msgs))

    @base.net_test
    def test_fail_msg(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!ud aaoihfeoifheofiehfoeifhe')
        self.assertEqual('No idea :(', self._proto.msgs[0][2])

def main():
    unittest.main()

if __name__ == '__main__':
    main()
