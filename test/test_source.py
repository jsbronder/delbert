import os
import unittest

import base

class SourceTester(unittest.TestCase):
    def setUp(self):
        self.config = {
            'responses': ['response'],
            'url' : 'http://url.com',
            'pre_verbs': ['make', 'modify'],
            'post_verbs': ['should'],
        }

        self._plugin = base.load_plugin('source.py', 'Source', config=self.config, seed=0)
        self._proto = base.TestProto([self._plugin])

    def test_passive(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '%s should blah' % (base.TEST_NICK,))
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0],
            ('msg', base.TEST_CHANNEL, '%s, %s' % (self.config['responses'][0], self.config['url'])))

    def test_passive2(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'blah %s should blah' % (base.TEST_NICK,))
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0],
            ('msg', base.TEST_CHANNEL, '%s, %s' % (self.config['responses'][0], self.config['url'])))

    def test_passive3(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'make %s do' % (base.TEST_NICK,))
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0],
            ('msg', base.TEST_CHANNEL, '%s, %s' % (self.config['responses'][0], self.config['url'])))

    def test_passive4(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'make %s' % (base.TEST_NICK,))
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0],
            ('msg', base.TEST_CHANNEL, '%s, %s' % (self.config['responses'][0], self.config['url'])))

    def test_no_passive(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'make blah%s' % (base.TEST_NICK,))
        self.assertEqual(0, len(self._proto.msgs))

    def test_no_passive2(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'blah%s should' % (base.TEST_NICK,))
        self.assertEqual(0, len(self._proto.msgs))

    def test_no_passive3(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '%sblah should' % (base.TEST_NICK,))
        self.assertEqual(0, len(self._proto.msgs))

    def test_no_passive4(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'make %sblah' % (base.TEST_NICK,))
        self.assertEqual(0, len(self._proto.msgs))

    def test_no_passive5(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '%s' % (base.TEST_NICK,))
        self.assertEqual(0, len(self._proto.msgs))

    def test_no_passive6(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, ' %s' % (base.TEST_NICK,))
        self.assertEqual(0, len(self._proto.msgs))

    def test_no_passive7(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, ' %s ' % (base.TEST_NICK,))
        self.assertEqual(0, len(self._proto.msgs))

    def test_no_passive8(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '%s shouldblah' % (base.TEST_NICK,))
        self.assertEqual(0, len(self._proto.msgs))


    def cmd(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!source')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('msg', base.TEST_CHANNEL, self.config['url']))


def main():
    unittest.main()

if __name__ == '__main__':
    main()
