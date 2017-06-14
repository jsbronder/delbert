import requests
from twisted.python import log

import delbert.plugin


class Startup(delbert.plugin.Plugin):
    def __init__(self, config={}):
        super(Startup, self).__init__('startup')
        self._config = config

    def query_startup(self):
        """
        Query the startup generator.

        @return  - a pretty sweet business idea bro!
        """
        try:
            html = requests.get(
                'http://itsthisforthat.com/api.php?text',
                verify=False)
        except requests.exceptions.RequestException, e:
            log.err(str(e))
            return

        return html.content.lower().capitalize()

    @delbert.plugin.irc_command('generate startup ideas')
    def startup(self, user, channel, args):
        msg = self.query_startup()

        if channel == self.nickname:
            n = delbert.plugin.get_nick(user)
            self._proto.send_msg(n, msg)
        else:
            self._proto.send_msg(channel, msg)
