import json
import unittest

import responses

import base
import requests

class HumanIdTester(unittest.TestCase):
    def setUp(self):
        self._plugin = base.load_plugin('humanid.py', 'HumanId')
        self._proto = base.TestProto([self._plugin])

    @base.net_test
    def test_query_real(self):
        m = self._plugin.get_some()
        self.assertTrue(len(m) > 0)

    @responses.activate
    def test_query(self):
        ret = {'text': 'test response'}
        base.create_json_response('.*amazonaws.*', ret)

        m = self._plugin.get_some()
        self.assertEqual('test response', m)

    @responses.activate
    def test_msg(self):
        ret = 'dr sugary booklet feat phat rule'
        base.create_json_response('.*amazonaws.*', {'text': ret})

        self._proto.privmsg('tester', base.TEST_CHANNEL, '!humanid')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0][2], ret)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
