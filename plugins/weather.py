import errno
import types

import requests
from twisted.python import log

class Weather(Plugin):
    """
    Plugin that handles looking up weather at various locations.
    """

    def __init__(self, config={}):
        super(Weather, self).__init__('weather')
        self._api_key = None

        if 'api_key' in config:
            self._api_key = config['api_key']
        else:
            log.err('No "weather.api_key" specified in config')

    @staticmethod
    def geoip(ip):
        """
        Lookup a physical location based on ip address.

        @param ip   - ip address to lookup.
        @return     - tuple (region_code, city) based on ip address.
        """
        try:
            req = requests.get('http://www.telize.com/geoip/%s' % (ip,))
            req.raise_for_status()
        except requests.exceptions.RequestException, e:
            log.err('Failed to get location for %s: %s' % (ip, str(e)))
            raise IOError(errno.EIO, 'Failed to get location for %s' % (ip,))

        return (req.json()['region_code'], req.json()['city'])

    @staticmethod
    def autocomplete(string):
        """
        Autocomplete a string to the best fit location.

        @param string   - base string to use for lookup.
        @return         - best fit location based on specified string.
        """
        try:
            req = requests.get(
                'http://autocomplete.wunderground.com/aq',
                params = {'query': string})
            req.raise_for_status()
        except requests.exceptions.RequestException, e:
            log.err('Failed to autocomplete "%s": %s' % (string, str(e)))
            raise IOError(errno.EIO, 'Failed to autocomplete "%s"' % (string,))

        if len(req.json()['RESULTS']) == 0:
            log.err('No results for autocompletion of "%s"' % (string,))
            raise IOError(errno.EIO, 'Failed to autocomplete "%s"' % (string,))

        return req.json()['RESULTS'][0]['l']

    def get_weather(self, location):
        """
        Get weather for a specified wunderground location.

        @location   - wunderground specific mapping to a location.
        @return     - mapping of weather types to current conditions.
        """
        try:
            url = 'http://api.wunderground.com/api/%s/conditions%s.json' % (
                    self._api_key, location)
        except IOError:
            return

        try:
            req = requests.get(url)
            req.raise_for_status()
        except requests.exceptions.RequestException, e:
            log.err(str(e))
            return

        return req.json()

    @irc_command('get weather for specified location or based your ip')
    def weather(self, user, channel, args):
        send_to = get_nick(user) if channel == self.nickname else channel

        if args == '':
            host = get_host(user)
            if '/' in host:
                self._proto.send_msg(send_to, "I can't look up a masked host, so, IT'S GONNA RAIN!")
                return

            try:
                args = self.geoip(get_host(user))
            except IOError:
                self._proto.send_msg(send_to, "IT'S GONNA RAIN!")
                return

        if self._api_key is None:
            self._proto.send_msg(send_to, 'Cannot lookup weather without a wunderground api key')
            return

        try:
            location = self.autocomplete(args)
            weather = self.get_weather(location)
        except IOError:
            self._proto.send_msg(send_to, "IT'S GONNA RAIN!")
            return

        try:
            ret = "%s, %s, %s, Humidity: %s, Wind: %s, Feels like: %s" % (
                weather['current_observation']['display_location']['full'],
                weather['current_observation']['weather'],
                weather['current_observation']['temperature_string'],
                weather['current_observation']['relative_humidity'],
                weather['current_observation']['wind_string'],
                weather['current_observation']['feelslike_string'],)
        except KeyError, e:
            log.err('Failed to parse %s: %s' % (weather, e))
            self._proto.send_msg(send_to, "IT'S GONNA RAIN!")
            return

        self._proto.send_msg(send_to, ret)

