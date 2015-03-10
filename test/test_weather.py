import contextlib
import os
import unittest

import base

API_FILE = os.path.join(
    os.path.realpath(os.path.dirname(__file__)),
    'db', 'weather-api-key')

FAKE_FORECAST = {u'txt_forecast': {u'date': u'2:00 PM PDT',
        u'forecastday': [{u'fcttext': u'Partly cloudy in the morning, then clear. High of 68F. Breezy. Winds from the West at 10 to 25 mph.',
        u'fcttext_metric': u'Partly cloudy in the morning, then clear. High of 20C. Windy. Winds from the West at 20 to 35 km/h.',
        u'icon': u'partlycloudy',
        u'icon_url': u'http://icons-ak.wxug.com/i/c/k/partlycloudy.gif',
        u'period': 0,
        u'pop': u'0',
        u'title': u'Tuesday'},
       {u'fcttext': u'Mostly cloudy. Fog overnight. Low of 50F. Winds from the WSW at 5 to 15 mph.',
        u'fcttext_metric': u'Mostly cloudy. Fog overnight. Low of 10C. Breezy. Winds from the WSW at 10 to 20 km/h.',
        u'icon': u'partlycloudy',
        u'icon_url': u'http://icons-ak.wxug.com/i/c/k/partlycloudy.gif',
        u'period': 1,
        u'pop': u'0',
        u'title': u'Tuesday Night'},
       {u'fcttext': u'Mostly cloudy. Fog early. High of 72F. Winds from the WSW at 10 to 15 mph.',
        u'fcttext_metric': u'Mostly cloudy. Fog early. High of 22C. Breezy. Winds from the WSW at 15 to 20 km/h.',
        u'icon': u'partlycloudy',
        u'icon_url': u'http://icons-ak.wxug.com/i/c/k/partlycloudy.gif',
        u'period': 2,
        u'pop': u'0',
        u'title': u'Wednesday'},
       {u'fcttext': u'Overcast. Fog overnight. Low of 54F. Winds from the WSW at 5 to 15 mph.',
        u'fcttext_metric': u'Overcast. Fog overnight. Low of 12C. Breezy. Winds from the WSW at 10 to 20 km/h.',
        u'icon': u'mostlycloudy',
        u'icon_url': u'http://icons-ak.wxug.com/i/c/k/mostlycloudy.gif',
        u'period': 3,
        u'pop': u'0',
        u'title': u'Wednesday Night'},
       {u'fcttext': u'Overcast in the morning, then partly cloudy. Fog early. High of 72F. Winds from the WSW at 10 to 15 mph.',
        u'fcttext_metric': u'Overcast in the morning, then partly cloudy. Fog early. High of 22C. Breezy. Winds from the WSW at 15 to 25 km/h.',
        u'icon': u'partlycloudy',
        u'icon_url': u'http://icons-ak.wxug.com/i/c/k/partlycloudy.gif',
        u'period': 4,
        u'pop': u'0',
        u'title': u'Thursday'},
       {u'fcttext': u'Partly cloudy in the evening, then overcast. Fog overnight. Low of 54F. Winds from the WNW at 5 to 15 mph.',
        u'fcttext_metric': u'Partly cloudy in the evening, then overcast. Fog overnight. Low of 12C. Breezy. Winds from the WNW at 10 to 20 km/h.',
        u'icon': u'partlycloudy',
        u'icon_url': u'http://icons-ak.wxug.com/i/c/k/partlycloudy.gif',
        u'period': 5,
        u'pop': u'0',
        u'title': u'Thursday Night'},
       {u'fcttext': u'Overcast in the morning, then partly cloudy. Fog early. High of 68F. Winds from the West at 5 to 15 mph.',
        u'fcttext_metric': u'Overcast in the morning, then partly cloudy. Fog early. High of 20C. Breezy. Winds from the West at 10 to 20 km/h.',
        u'icon': u'partlycloudy',
        u'icon_url': u'http://icons-ak.wxug.com/i/c/k/partlycloudy.gif',
        u'period': 6,
        u'pop': u'0',
        u'title': u'Friday'},]}}

def fake_autocomplete(*args, **kwds):
    return 'fake_location'

def fake_forecast(*args, **kwds):
    return FAKE_FORECAST


class WeatherTester(unittest.TestCase):
    @contextlib.contextmanager
    def fake_functions(self):
        get_forecast = self._plugin.get_forecast
        autocomplete = self._plugin.autocomplete

        self._plugin.get_forecast = fake_forecast
        self._plugin.autocomplete = fake_autocomplete

        yield

        self._plugin.get_forecast = get_forecast 
        self._plugin.autocomplete = autocomplete 

    def setUp(self):
        config = {
            'api_key': open(API_FILE).read().strip(),
        }
        self._plugin = base.load_plugin('weather.py', 'Weather', config=config)
        self._proto = base.TestProto([self._plugin])
        self._boston = '/q/zmw:02101.1.99999'
        self._newry_me = '/q/zmw:04261.1.99999'
        self._ip = '209.6.43.0'

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    @base.net_test
    def test_autocomplete(self):
        m = self._plugin.autocomplete('boston')
        self.assertEqual(m, self._boston)

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    @base.net_test
    def test_autocomplete_multistring(self):
        m = self._plugin.autocomplete('newry me')
        self.assertEqual(m, self._newry_me)

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    @base.net_test
    def test_get_weather(self):
        m = self._plugin.get_weather(self._boston)
        loc = m['current_observation']['display_location']['full']
        self.assertEqual(loc, 'Boston, MA')

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    @base.net_test
    def test_geoip(self):
        m = self._plugin.geoip(self._ip)
        self.assertEqual(m, ('MA', 'Somerville'))

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    @base.net_test
    def test_msg(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!weather boston')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertTrue(self._proto.msgs[0][2].startswith('Boston, MA, '))

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    @base.net_test
    def test_msg_multistring(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!weather newry me')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertTrue(self._proto.msgs[0][2].startswith('Newry, ME, '))

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    @base.net_test
    def test_host(self):
        self._proto.privmsg('tester!blah@%s' % (self._ip,), base.TEST_CHANNEL, '!weather')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertTrue(self._proto.msgs[0][2].startswith('Somerville, MA, '))

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    @base.net_test
    def test_masked_host(self):
        self._proto.privmsg('tester!blah@some/mask', base.TEST_CHANNEL, '!weather')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertTrue(self._proto.msgs[0][2].endswith('maskedhostville'))

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    @base.net_test
    def test_fail_autocomplete(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!weather aohicehcaoiehfoaiehfe')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertTrue(self._proto.msgs[0][2].startswith('Nice try,'))

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    @base.net_test
    def test_get_forecast(self):
        m = self._plugin.get_forecast(self._boston)
        self.assertEqual(8, len(m['txt_forecast']['forecastday']))

    def test_forecast_response(self):
        with self.fake_functions():
            self._proto.privmsg('tester', base.TEST_CHANNEL, '!forecast boston')
            for i, txt in enumerate(FAKE_FORECAST['txt_forecast']['forecastday']):
                self.assertEqual(self._proto.msgs[i][0], 'notice')
                self.assertTrue(self._proto.msgs[i][2].endswith(txt['fcttext']))


def main():
    unittest.main()

if __name__ == '__main__':
    main()
