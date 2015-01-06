import os
import unittest

import base

class CAHTester(unittest.TestCase):
    def setUp(self):
        cdir = os.path.realpath(os.path.dirname(__file__))
        config = {
            'white': os.path.join(cdir, 'db', 'cah-white.txt'),
            'black': os.path.join(cdir, 'db', 'cah-black.txt'),
        }
        self._plugin = base.load_plugin('cah.py', 'CardsAgainstHumanity', config=config, seed=0)
        self._proto = base.TestProto([self._plugin])
        self._msg = 'Some question is "answered"'

    def test_query(self):
        m = self._plugin.get_msg()
        self.assertEqual(m, self._msg)

    def test_msg(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!cah')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('msg', base.TEST_CHANNEL, self._msg))

def main():
    unittest.main()

if __name__ == '__main__':
    main()
