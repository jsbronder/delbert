import os
import unittest

import base

API_FILE = os.path.join(
    os.path.realpath(os.path.dirname(__file__)),
    'db', 'weather-api-key')

class WeatherTester(unittest.TestCase):
    def setUp(self):
        config = {
            'api_key': open(API_FILE).read().strip(),
        }
        self._plugin = base.load_plugin('weather.py', 'Weather', config=config)
        self._proto = base.TestProto([self._plugin])
        self._boston = '/q/zmw:02101.1.99999'
        self._ip = '209.6.43.0'

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    def test_autocomplete(self):
        m = self._plugin.autocomplete('boston')
        self.assertEqual(m, self._boston)

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    def test_get_weather(self):
        m = self._plugin.get_weather(self._boston)
        loc = m['current_observation']['display_location']['full']
        self.assertEqual(loc, 'Boston, MA')

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    def test_geoip(self):
        m = self._plugin.geoip(self._ip)
        self.assertEqual(m, ('MA', 'Somerville'))

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    def test_msg(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!weather boston')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertTrue(self._proto.msgs[0][2].startswith('Boston, MA, '))

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    def test_host(self):
        self._proto.privmsg('tester!blah@%s' % (self._ip,), base.TEST_CHANNEL, '!weather')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertTrue(self._proto.msgs[0][2].startswith('Somerville, MA, '))

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    def test_masked_host(self):
        self._proto.privmsg('tester!blah@some/mask', base.TEST_CHANNEL, '!weather')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertTrue(self._proto.msgs[0][2].endswith('IT\'S GONNA RAIN!'))

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    def test_fail_autocomplete(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!weather aohicehcaoiehfoaiehfe')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('msg', base.TEST_CHANNEL, 'IT\'S GONNA RAIN!'))


def main():
    unittest.main()

if __name__ == '__main__':
    main()
