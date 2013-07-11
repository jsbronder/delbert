import errno
import types

import requests
from twisted.python import log

INSTANCE = None

class Weather(object):
    def __init__(self):
        try:
            self._api_key = config['api_key']
        except:
            log.err('No "weather.api_key" specified in config')
            raise

    @staticmethod
    def geoip(ip):
        try:
            req = requests.get('http://freegeoip.net/json/%s' % (ip,))
            req.raise_for_status()
        except requests.exceptions.RequestException, e:
            log.err('Failed to get location for %s: %s' % (ip, str(e)))
            raise IOError(errno.EIO, 'Failed to get location for %s' % (ip,))

        return (req.json['region_code'], req.json['city'])

    @staticmethod
    def autocomplete(string):
        try:
            req = requests.get(
                'http://autocomplete.wunderground.com/aq',
                params = {'query': string})
            req.raise_for_status()
        except requests.exceptions.RequestException, e:
            log.err('Failed to autocomplete "%s": %s' % (string, str(e)))
            raise IOError(errno.EIO, 'Failed to autocomplete "%s"' % (string,))

        if len(req.json['RESULTS']) == 0:
            log.err('No results for autocompletion of "%s"' % (string,))
            raise IOError(errno.EIO, 'Failed to autocomplete "%s"' % (string,))

        return req.json['RESULTS'][0]['l']


    def weather(self, user, arg):
        if len(arg) == 0:
            host = get_host(user)
            if '/' in host:
                return "I can't look up a masked host, so, IT'S GONNA RAIN!"

            try:
                arg = self.geoip(get_host(user))
            except IOError:
                return "IT'S GONNA RAIN!"

        try:
            url = 'http://api.wunderground.com/api/%s/conditions%s.json' % (
                    self._api_key, self.autocomplete(arg))
        except IOError:
            return "IT'S GONNA RAIN!"

        try:
            req = requests.get(url)
            req.raise_for_status()
        except requests.exceptions.RequestException, e:
            log.err('Failed to get weather for "%s"' % (arg,))
            return "IT'S GONNA RAIN!"

        try:
            ret = "%s, %s, %s, Humidity: %s, Wind: %s, Feels like: %s" % (
                req.json['current_observation']['display_location']['full'],
                req.json['current_observation']['weather'],
                req.json['current_observation']['temperature_string'],
                req.json['current_observation']['relative_humidity'],
                req.json['current_observation']['wind_string'],
                req.json['current_observation']['feelslike_string'],)
        except KeyError, e:
            log.err('Failed to parse %s: %s' % (str(req.json), e))
            return "IT'S GONNA RAIN!"

        return ret


def init():
    global INSTANCE
    INSTANCE = Weather()

def cmd_weather(proto, user, channel, msg):
    ret = INSTANCE.weather(user, msg)
    if isinstance(ret, types.UnicodeType):
        ret = ret.encode('utf-8')

    proto.msg(channel, ret)

