import os
import unittest

import base

class SprintTest(unittest.TestCase):
    def setUp(self):
        cdir = os.path.realpath(os.path.dirname(__file__))
        config = {'sprint': os.path.join(cdir, 'db', 'sprint.yaml')}
        self._plugin = base.load_plugin('sprint.py', 'SprintGoals', config=config, seed=0)
        self._proto = base.TestProto([self._plugin])
        self._msg = 'adverb verb adjective noun'

    def test_msg(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!sprint')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('msg', base.TEST_CHANNEL, self._msg))

def main():
    unittest.main()

if __name__ == '__main__':
    main()
