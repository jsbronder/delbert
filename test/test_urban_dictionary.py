import json
import unittest

import responses

import base

class UDTester(unittest.TestCase):
    def setUp(self):
        self._plugin = base.load_plugin('urban_dictionary.py', 'UrbanDictionary')
        self._proto = base.TestProto([self._plugin])

    @base.net_test
    def test_query_real(self):
        m = self._plugin.query('test')
        self.assertTrue(m.startswith('The word all students fear.'))

    @responses.activate
    def test_query(self):
        ret = {'definition': 'test response'}
        base.create_json_response('.*urbandictionary.*', {'list': [ret]})

        m = self._plugin.query('test')
        self.assertEqual('test response', m)

    @responses.activate
    def test_msg(self):
        ret = {'definition': 'test response'}
        base.create_json_response('.*urbandictionary.*', {'list': [ret]})

        self._proto.privmsg('tester', base.TEST_CHANNEL, '!ud test')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0][2], 'test:  test response')

    @responses.activate
    def test_compound_msg(self):
        ret = {'definition': 'test response'}

        def f(request):
            req = request.url.split('=')[1]
            if req == 'compound+message':
                return (200, {}, json.dumps({'list': [ret]}))
            else:
                return (500, {}, json.dumps({}))

        responses.add_callback(responses.GET,
                url='http://api.urbandictionary.com/v0/define',
                callback=f)

        self._proto.privmsg('tester', base.TEST_CHANNEL, '!ud compound message')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0][2], 'compound message:  test response')

    @responses.activate
    def test_url_escape(self):
        ret = {'definition': 'test response'}

        def f(request):
            req = request.url.split('=')[1]
            if req == 'comp%23ound+message%2B':
                return (200, {}, json.dumps({'list': [ret]}))
            else:
                return (500, {}, json.dumps({}))

        responses.add_callback(responses.GET,
                url='http://api.urbandictionary.com/v0/define',
                callback=f)

        self._proto.privmsg('tester', base.TEST_CHANNEL, '!ud comp#ound message+')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0][2], 'comp#ound message+:  test response')

    @responses.activate
    def test_fail_msg(self):
        base.create_json_response('.*urbandictionary.*', {})
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!ud blah')
        self.assertEqual('No idea :(', self._proto.msgs[0][2])

def main():
    unittest.main()

if __name__ == '__main__':
    main()
