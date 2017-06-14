import errno

import requests
from twisted.python import log

import delbert.plugin


class Weather(delbert.plugin.Plugin):
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
                params={'query': string})
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

    def get_forecast(self, location):
        """
        Get the 3 day forecast for a specified wunderground location.

        @param location - wunderground specific mapping to a location.
        @return         - map of forecast,  see
                          http://www.wunderground.com/weather/api/d/docs?d=data/forecast&MR=1
        """
        try:
            url = 'http://api.wunderground.com/api/%s/forecast%s.json' % (
                    self._api_key, location)
        except IOError:
            return

        try:
            req = requests.get(url)
            req.raise_for_status()
        except requests.exceptions.RequestException as e:
            log.err(str(e))
            return

        return req.json()['forecast']

    def _get_user_location(self, user, channel, args):
        """
        Lookup the request location.  If the user passed any arguments, try to
        autocomplete based on those, otherwise fallback to running geoip on the
        users host.

        On errors snide remarks^B^Bmessages will be sent to user.

        @param user     - full username
        @param channel  - current channel
        @param args     - any arguments passed by the user
        @return         - A location string fit to be passed to the
                          wunderground API or None on Failure.
        """
        if channel == self.nickname:
            send_to = delbert.plugin.get_nick(user)
        else:
            send_to = channel

        if args == '':
            host = delbert.plugin.get_host(user)
            if '/' in host:
                self._proto.send_msg(
                    send_to,
                    'I hear the weather is nice in maskedhostville')
                return

            try:
                args = self.geoip(host)
            except IOError:
                self._proto.send_msg(
                    send_to,
                    'Lucky stiff, the feds can\'t trace your ip.'
                    '  Or at least the free service I use can\'t.')
                return

        if self._api_key is None:
            self._proto.send_msg(
                send_to,
                'Cannot lookup weather without a wunderground api key')
            return

        try:
            location = self.autocomplete(args)
        except IOError:
            self._proto.send_msg(
                send_to,
                'Nice try, "%s" isn\'t a real location' % (' '.join(args),))
            return

        return location

    @delbert.plugin.irc_command(
        'get weather for specified location or based your ip')
    def weather(self, user, channel, args):
        location = self._get_user_location(user, channel, args)
        if location is None:
            return

        if channel == self.nickname:
            send_to = delbert.plugin.get_nick(user)
        else:
            send_to = channel

        try:
            weather = self.get_weather(location)
        except IOError:
            self._proto.send_msg(send_to, 'Meh, look it up yourself')
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

    @delbert.plugin.irc_command(
        'get forecast for specified location or based on your ip')
    def forecast(self, user, channel, args):
        location = self._get_user_location(user, channel, args)
        if location is None:
            return

        if channel == self.nickname:
            send_to = delbert.plugin.get_nick(user)
        else:
            send_to = channel

        try:
            forecast = self.get_forecast(location)
        except IOError:
            self._proto.send_msg(send_to, 'Nope, no forecast for you')

        for day in forecast['txt_forecast']['forecastday']:
            try:
                self._proto.send_notice(
                    send_to,
                    '%-15s %s' % (day['title'] + ':', day['fcttext']))
            except KeyError as e:
                log.err('Failed to parse %s: %s' % (forecast, e))
                return
