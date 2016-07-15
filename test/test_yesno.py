import unittest

import responses

import base

class YesNoTester(unittest.TestCase):
    def setUp(self):
        self._plugin = base.load_plugin('yesno.py', 'YesNo')
        self._proto = base.TestProto([self._plugin])

    @base.net_test
    def test_query_real(self):
        answer, image = self._plugin.query()

        self.assertIn(answer, ('yes', 'no', 'maybe'))
        self.assertTrue(image.startswith('http://yesno.wtf/assets/%s' % (answer,)))

    @responses.activate
    def test_query(self):
        resp = {
            'answer': 'yes',
            'image': 'http://some.image/url',
        }
        base.create_json_response('http://yesno.wtf/api', resp)

        answer, image = self._plugin.query()
        self.assertEqual(answer, resp['answer'])
        self.assertEqual(image, resp['image'])

    @responses.activate
    def test_msg(self):
        resp = {
            'answer': 'yes',
            'image': 'http://some.image/url',
        }
        base.create_json_response('http://yesno.wtf/api', resp)

        self._proto.privmsg('tester', base.TEST_CHANNEL, '!yesno')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(
                self._proto.msgs[0][2],
                '%s! (%s)' % (resp['answer'].upper(), resp['image']))

    @responses.activate
    def test_respond(self):
        msg_count = 0
        resp = {
            'answer': 'yes',
            'image': 'http://some.image/url',
        }
        base.create_json_response('http://yesno.wtf/api', resp)

        self._plugin._chance = 1
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'Not a question')
        self.assertEqual(msg_count, len(self._proto.msgs))

        self._proto.privmsg('tester', base.TEST_CHANNEL, 'Is a question? in here')
        msg_count += 1
        self.assertEqual(msg_count, len(self._proto.msgs))
        self.assertEqual(
                self._proto.msgs[msg_count-1][2],
                '%s! (%s)' % (resp['answer'].upper(), resp['image']))

        self._plugin._chance = 0
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'All the questions? have no? chance?????')
        self.assertEqual(msg_count, len(self._proto.msgs))


def main():
    unittest.main()

if __name__ == '__main__':
    main()
