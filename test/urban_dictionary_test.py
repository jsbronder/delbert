import unittest

import base

class UDTester(unittest.TestCase):
    def setUp(self):
        self._plugin = base.load_plugin('urban_dictionary.py', 'UrbanDictionary')
        self._proto = base.TestProto([self._plugin])

    def test_query(self):
        m = self._plugin.query('test')
        self.assertEqual('A process for testing things', m)

    def test_msg(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!ud test')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(
            self._proto.msgs[0][2],
            'test:  A process for testing things')

def main():
    unittest.main()

if __name__ == '__main__':
    main()
