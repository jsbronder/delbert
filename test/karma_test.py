import os
import tempfile
import unittest

import base

class KarmaTester(unittest.TestCase):
    def setUp(self):
        fd, self._path = tempfile.mkstemp()
        os.close(fd)

        config = {
            'ds': self._path,
        }
        self._plugin = base.load_plugin('karma.py', 'Karma', config=config)
        self._proto = base.TestProto([self._plugin])

    def tearDown(self):
        if os.path.exists(self._path):
            os.unlink(self._path)

    def test_add(self):
        self._plugin.add('blah', 'me')
        self.assertEqual(self._plugin.get_karma('blah'), {'me': 1})

    def test_sub(self):
        self._plugin.neg('blah', 'me')
        self.assertEqual(self._plugin.get_karma('blah'), {'me': -1})

    def test_passive(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'me++')
        self.assertEqual(self._plugin.get_karma(base.TEST_CHANNEL), {'me': 1})

        self._proto.privmsg('tester', base.TEST_CHANNEL, 'you--')
        self.assertEqual(self._plugin.get_karma(base.TEST_CHANNEL), {'me': 1, 'you': -1})

    def test_self_modify(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'tester++')
        self.assertEqual(self._plugin.get_karma(base.TEST_CHANNEL), {})

        self._proto.privmsg('tester', base.TEST_CHANNEL, 'tester--')
        self.assertEqual(self._plugin.get_karma(base.TEST_CHANNEL), {'tester': -1})

    def test_cmd(self):
        self._plugin.add(base.TEST_CHANNEL, 'me')
        self._plugin.neg(base.TEST_CHANNEL, 'you')
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!karma')

        self.assertEqual(self._proto.msgs[0],
                ('notice', base.TEST_CHANNEL, '%s karma:' % (base.TEST_CHANNEL,)))

        self.assertEqual(3, len(self._proto.msgs))

    def test_cmd2(self):
        self._plugin.add('blah', 'me')
        self._plugin.neg('blah', 'you')
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!karma blah')

        self.assertEqual(self._proto.msgs[0],
                ('notice', base.TEST_CHANNEL, 'blah karma:'))

        self.assertEqual(3, len(self._proto.msgs))

def main():
    unittest.main()

if __name__ == '__main__':
    main()
