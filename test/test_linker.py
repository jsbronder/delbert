import unittest

import base

class LinkerTester(unittest.TestCase):
    def setUp(self):
        self._linker = base.load_plugin('linker.py', 'Linker')
        self._proto = base.TestProto([self._linker])

    @base.net_test
    def test_title(self):
        m = self._linker.get_title('http://www.google.com')
        self.assertEqual(m, 'Link: Google')

    @base.net_test
    def test_link(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'http://www.google.com')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('msg', base.TEST_CHANNEL, 'Link: Google'))

    @base.net_test
    def test_inside_link(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'check out http://www.google.com this link')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('msg', base.TEST_CHANNEL, 'Link: Google'))

    @base.net_test
    def test_multiple_link(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'http://www.google.com ' * 2)
        self.assertEqual(2, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('msg', base.TEST_CHANNEL, 'Link: Google'))
        self.assertEqual(self._proto.msgs[1], ('msg', base.TEST_CHANNEL, 'Link: Google'))


def main():
    unittest.main()

if __name__ == '__main__':
    main()
