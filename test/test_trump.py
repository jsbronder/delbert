import unittest

import base

class TrumpTester(unittest.TestCase):
    def setUp(self):
        self.config = {
            'verbosity': 1.0,
        }

        self._plugin = base.load_plugin('trump.py', 'Trump', config=self.config, seed=0)
        self._proto = base.TestProto([self._plugin])

    def test_passive(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'why?')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0][2], "All I know is what's on the internet.")


def main():
    unittest.main()

if __name__ == '__main__':
    main()
