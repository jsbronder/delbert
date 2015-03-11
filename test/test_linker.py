import unittest

import responses

import base

class LinkerTester(unittest.TestCase):
    def setUp(self):
        self._linker = base.load_plugin('linker.py', 'Linker')
        self._proto = base.TestProto([self._linker])

    @responses.activate
    def test_title(self):
        base.create_response('http://test.com', '<body><title>blah</title></body>')
        m = self._linker.get_title('http://test.com')
        self.assertEqual(m, 'Link: blah')

    @responses.activate
    def test_link(self):
        base.create_response('http://test.com', '<body><title>blah</title></body>')
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'http://test.com')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('msg', base.TEST_CHANNEL, 'Link: blah'))

    @responses.activate
    def test_inside_link(self):
        base.create_response('http://test.com', '<body><title>blah</title></body>')
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'check out http://test.com this link')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('msg', base.TEST_CHANNEL, 'Link: blah'))

    @responses.activate
    def test_multiple_link(self):
        base.create_response('http://test.com', '<body><title>blah</title></body>')
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'http://test.com ' * 2)
        self.assertEqual(2, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('msg', base.TEST_CHANNEL, 'Link: blah'))
        self.assertEqual(self._proto.msgs[1], ('msg', base.TEST_CHANNEL, 'Link: blah'))


def main():
    unittest.main()

if __name__ == '__main__':
    main()
