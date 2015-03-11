import contextlib
import json
import os
import unittest

import responses

import base

API_FILE = os.path.join(
    os.path.realpath(os.path.dirname(__file__)),
    'db', 'weather-api-key')

FAKE_FORECAST = {
    u'txt_forecast':
        {u'date': u'2:00 PM PDT',
            u'forecastday':
            [
                {
                    u'fcttext': u'Partly cloudy in the morning, then clear. High of 68F. Breezy. Winds from the West at 10 to 25 mph.',
                    u'fcttext_metric': u'Partly cloudy in the morning, then clear. High of 20C. Windy. Winds from the West at 20 to 35 km/h.',
                    u'icon': u'partlycloudy',
                    u'icon_url': u'http://icons-ak.wxug.com/i/c/k/partlycloudy.gif',
                    u'period': 0,
                    u'pop': u'0',
                    u'title': u'Tuesday'
                },
                {
                   u'fcttext': u'Mostly cloudy. Fog overnight. Low of 50F. Winds from the WSW at 5 to 15 mph.',
                   u'fcttext_metric': u'Mostly cloudy. Fog overnight. Low of 10C. Breezy. Winds from the WSW at 10 to 20 km/h.',
                   u'icon': u'partlycloudy',
                   u'icon_url': u'http://icons-ak.wxug.com/i/c/k/partlycloudy.gif',
                   u'period': 1,
                   u'pop': u'0',
                   u'title': u'Tuesday Night'
                },
           {
                u'fcttext': u'Mostly cloudy. Fog early. High of 72F. Winds from the WSW at 10 to 15 mph.',
                u'fcttext_metric': u'Mostly cloudy. Fog early. High of 22C. Breezy. Winds from the WSW at 15 to 20 km/h.',
                u'icon': u'partlycloudy',
                u'icon_url': u'http://icons-ak.wxug.com/i/c/k/partlycloudy.gif',
                u'period': 2,
                u'pop': u'0',
                u'title': u'Wednesday'
            },
            {
                u'fcttext': u'Overcast. Fog overnight. Low of 54F. Winds from the WSW at 5 to 15 mph.',
                u'fcttext_metric': u'Overcast. Fog overnight. Low of 12C. Breezy. Winds from the WSW at 10 to 20 km/h.',
                u'icon': u'mostlycloudy',
                u'icon_url': u'http://icons-ak.wxug.com/i/c/k/mostlycloudy.gif',
                u'period': 3,
                u'pop': u'0',
                u'title': u'Wednesday Night'
            },
            {
               u'fcttext': u'Overcast in the morning, then partly cloudy. Fog early. High of 72F. Winds from the WSW at 10 to 15 mph.',
                u'fcttext_metric': u'Overcast in the morning, then partly cloudy. Fog early. High of 22C. Breezy. Winds from the WSW at 15 to 25 km/h.',
                u'icon': u'partlycloudy',
                u'icon_url': u'http://icons-ak.wxug.com/i/c/k/partlycloudy.gif',
                u'period': 4,
                u'pop': u'0',
                u'title': u'Thursday'
            },
            {
                u'fcttext': u'Partly cloudy in the evening, then overcast. Fog overnight. Low of 54F. Winds from the WNW at 5 to 15 mph.',
                u'fcttext_metric': u'Partly cloudy in the evening, then overcast. Fog overnight. Low of 12C. Breezy. Winds from the WNW at 10 to 20 km/h.',
                u'icon': u'partlycloudy',
                u'icon_url': u'http://icons-ak.wxug.com/i/c/k/partlycloudy.gif',
                u'period': 5,
                u'pop': u'0',
                u'title': u'Thursday Night'},
            {
                    u'fcttext': u'Overcast in the morning, then partly cloudy. Fog early. High of 68F. Winds from the West at 5 to 15 mph.',
                u'fcttext_metric': u'Overcast in the morning, then partly cloudy. Fog early. High of 20C. Breezy. Winds from the West at 10 to 20 km/h.',
                u'icon': u'partlycloudy',
                u'icon_url': u'http://icons-ak.wxug.com/i/c/k/partlycloudy.gif',
                u'period': 6,
                u'pop': u'0',
                u'title': u'Friday'
            },
        ]
    }
}

FAKE_WEATHER = {
  'current_observation': {
        'image': {
            'url':'http://icons.wxug.com/graphics/wu2/logo_130x80.png',
            'title':'Weather Underground',
            'link':'http://www.wunderground.com'
        },
        'display_location': {
            'full':'Newry, ME',
            'city':'Newry',
            'state':'ME',
            'state_name':'Maine',
            'country':'US',
            'country_iso3166':'US',
            'zip':'04261',
            'magic':'1',
            'wmo':'99999',
            'latitude':'44.68947220',
            'longitude':'-71.01172638',
            'elevation':'563.00000000'
        },
        'observation_location': {
            'full':'Berlin, New Hampshire',
            'city':'Berlin',
            'state':'New Hampshire',
            'country':'US',
            'country_iso3166':'US',
            'latitude':'44.57611084',
            'longitude':'-71.17861176',
            'elevation':'1158 ft'
        },
        'estimated': {},
        'station_id':'KBML',
        'observation_time':'Last Updated on March 10, 11:52 PM EDT',
        'observation_time_rfc822':'Tue, 10 Mar 2015 23:52:00 -0400',
        'observation_epoch':'1426045920',
        'local_time_rfc822':'Wed, 11 Mar 2015 00:37:19 -0400',
        'local_epoch':'1426048639',
        'local_tz_short':'EDT',
        'local_tz_long':'America/New_York',
        'local_tz_offset':'-0400',
        'weather':'Mostly Cloudy',
        'temperature_string':'46 F (8 C)',
        'temp_f':46,
        'temp_c':8,
        'relative_humidity':'51%',
        'wind_string':'Calm',
        'wind_dir':'North',
        'wind_degrees':0,
        'wind_mph':0,
        'wind_gust_mph':0,
        'wind_kph':0,
        'wind_gust_kph':0,
        'pressure_mb':'1012',
        'pressure_in':'29.88',
        'pressure_trend':'-',
        'dewpoint_string':'29 F (-2 C)',
        'dewpoint_f':29,
        'dewpoint_c':-2,
        'heat_index_string':'NA',
        'heat_index_f':'NA',
        'heat_index_c':'NA',
        'windchill_string':'NA',
        'windchill_f':'NA',
        'windchill_c':'NA',
        'feelslike_string':'46 F (8 C)',
        'feelslike_f':'46',
        'feelslike_c':'8',
        'visibility_mi':'10.0',
        'visibility_km':'16.1',
        'solarradiation':'--',
        'UV':'0','precip_1hr_string':'-9999.00 in (-9999.00 mm)',
        'precip_1hr_in':'-9999.00',
        'precip_1hr_metric':'--',
        'precip_today_string':'0.00 in (0.0 mm)',
        'precip_today_in':'0.00',
        'precip_today_metric':'0.0',
        'icon':'mostlycloudy',
        'icon_url':'http://icons.wxug.com/i/c/k/nt_mostlycloudy.gif',
        'forecast_url':'http://www.wunderground.com/US/ME/Newry.html',
        'history_url':'http://www.wunderground.com/history/airport/KBML/2015/3/10/DailyHistory.html',
        'ob_url':'http://www.wunderground.com/cgi-bin/findweather/getForecast?query=44.57611084,-71.17861176',
        'nowcast':''
    }
}

class WeatherTester(unittest.TestCase):
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
    def test_autocomplete_real(self):
        m = self._plugin.autocomplete('boston')
        self.assertEqual(m, self._boston)

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    @base.net_test
    def test_autocomplete_multistring_real(self):
        m = self._plugin.autocomplete('newry me')
        self.assertEqual(m, self._newry_me)

    @responses.activate
    def test_autocomplete(self):
        base.create_json_response('.*wunderground.*', {'RESULTS': [{'l': self._boston}]})
        m = self._plugin.autocomplete('boston')
        self.assertEqual(m, self._boston)

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    @base.net_test
    def test_get_weather_real(self):
        m = self._plugin.get_weather(self._boston)
        loc = m['current_observation']['display_location']['full']
        self.assertEqual(loc, 'Boston, MA')

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    @base.net_test
    def test_geoip_real(self):
        m = self._plugin.geoip(self._ip)
        self.assertEqual(m, ('MA', 'Somerville'))

    @unittest.skipIf(not os.path.exists(API_FILE), 'No wunderground api key file found')
    @base.net_test
    def test_get_forecast_real(self):
        m = self._plugin.get_forecast(self._boston)
        self.assertEqual(8, len(m['txt_forecast']['forecastday']))

    @responses.activate
    def test_autocomplete_multistring(self):
        base.create_json_response('.*wunderground.*', {'RESULTS': [{'l': self._newry_me}]})
        m = self._plugin.autocomplete('newry me')
        self.assertEqual(m, self._newry_me)

    @responses.activate
    def test_get_weather(self):
        base.create_json_response('.*wunderground.*', FAKE_FORECAST)
        m = self._plugin.get_weather(self._boston)
        self.assertEqual(m, FAKE_FORECAST)

    @responses.activate
    def test_geoip(self):
        ret = {
            'region_code': 'test_region',
            'city': 'test_city'}
        base.create_json_response('.*telize.*', ret)

        m = self._plugin.geoip(self._ip)
        self.assertEqual(m, ('test_region', 'test_city'))

    @responses.activate
    def test_msg(self):
        base.create_json_response('.*autocomplete.*', {'RESULTS': [{'l': self._newry_me}]})
        base.create_json_response('.*api\.wunderground.*', FAKE_WEATHER)

        self._proto.privmsg('tester', base.TEST_CHANNEL, '!weather boston')
        self.assertEqual(1, len(self._proto.msgs))
        expected = "%s, %s, %s, Humidity: %s, Wind: %s, Feels like: %s" % (
                FAKE_WEATHER['current_observation']['display_location']['full'],
                FAKE_WEATHER['current_observation']['weather'],
                FAKE_WEATHER['current_observation']['temperature_string'],
                FAKE_WEATHER['current_observation']['relative_humidity'],
                FAKE_WEATHER['current_observation']['wind_string'],
                FAKE_WEATHER['current_observation']['feelslike_string'],)

        self.assertEqual(self._proto.msgs[0][2], expected)

    @responses.activate
    def test_msg_multistring(self):
        def f(request):
            req = request.url.split('=')[1]
            if req == 'newry+me':
                return (200, {}, json.dumps({'RESULTS': [{'l': self._newry_me}]}))

        responses.add_callback(responses.GET,
                url='http://autocomplete.wunderground.com/aq',
                callback=f)
        base.create_json_response('.*api\.wunderground.*', FAKE_WEATHER)

        self._proto.privmsg('tester', base.TEST_CHANNEL, '!weather newry me')
        self.assertEqual(1, len(self._proto.msgs))
        expected = "%s, %s, %s, Humidity: %s, Wind: %s, Feels like: %s" % (
                FAKE_WEATHER['current_observation']['display_location']['full'],
                FAKE_WEATHER['current_observation']['weather'],
                FAKE_WEATHER['current_observation']['temperature_string'],
                FAKE_WEATHER['current_observation']['relative_humidity'],
                FAKE_WEATHER['current_observation']['wind_string'],
                FAKE_WEATHER['current_observation']['feelslike_string'],)

        self.assertEqual(self._proto.msgs[0][2], expected)

    @responses.activate
    def test_host(self):
        class Closure(object):
            got_valid_request = False
        cls = Closure()

        def f(request):
            ret = {
                'region_code': 'test_region',
                'city': 'test_city'}

            if request.url.split('/')[-1] == self._ip:
                cls.got_valid_request = True

            return (200, {}, json.dumps(ret))

        responses.add_callback(responses.GET,
                url='http://www.telize.com/geoip/%s' % (self._ip,),
                callback=f)
        base.create_json_response('.*autocomplete.*', {'RESULTS': [{'l': self._newry_me}]})
        base.create_json_response('.*api\.wunderground.*', FAKE_WEATHER)

        self._proto.privmsg('tester!blah@%s' % (self._ip,), base.TEST_CHANNEL, '!weather')
        self.assertTrue(cls.got_valid_request)

    def test_masked_host(self):
        self._proto.privmsg('tester!blah@some/mask', base.TEST_CHANNEL, '!weather')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertTrue(self._proto.msgs[0][2].endswith('maskedhostville'))

    @responses.activate
    def test_fail_autocomplete(self):
        base.create_json_response('.*autocomplete.*', {'RESULTS': []})
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!weather fail')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertTrue(self._proto.msgs[0][2].startswith('Nice try,'))

    @responses.activate
    def test_forecast_response(self):
        base.create_json_response('.*autocomplete.*', {'RESULTS': [{'l': self._newry_me}]})
        base.create_json_response('.*api\.wunderground.*', {'forecast': FAKE_FORECAST})

        self._proto.privmsg('tester', base.TEST_CHANNEL, '!forecast boston')
        for i, txt in enumerate(FAKE_FORECAST['txt_forecast']['forecastday']):
            self.assertEqual(self._proto.msgs[i][0], 'notice')
            self.assertTrue(self._proto.msgs[i][2].endswith(txt['fcttext']))


def main():
    unittest.main()

if __name__ == '__main__':
    main()
