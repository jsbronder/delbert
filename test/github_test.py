import re
import unittest

import base

class GithubTester(unittest.TestCase):
    def setUp(self):
        self._plugin = base.load_plugin('github.py', 'Github')
        self._proto = base.TestProto([self._plugin])
        self._re = re.compile('^[0-9-]{10}T[0-9:]{8}Z:  \[[a-z]*\]')

    def test_query(self):
        m = self._plugin.status
        self.assertIsNotNone(self._re.search(m))

    def test_msg(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!github')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertIsNotNone(self._re.search(self._proto.msgs[0][2]))

def main():
    unittest.main()

if __name__ == '__main__':
    main()
