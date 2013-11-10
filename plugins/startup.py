import requests
from twisted.python import log

class Startup(Plugin):
    def __init__(self, config={}):
        super(Startup, self).__init__('startup')
        self._config = config

    def query_startup(self):
        """
        Query the startup generator.

        @return  - a pretty sweet business idea bro!
        """
        try:
            html = requests.get('http://itsthisforthat.com/api.php?text', verify=False)
        except requests.exceptions.RequestException, e:
            log.err(str(e))
            return

        return html.content.lower().capitalize()

    @irc_command('generate startup ideas')
    def startup(self, user, channel, args):
        msg = self.query_startup()

        if channel == self.nickname:
            self._proto.send_msg(get_nick(user), msg)
        else:
            self._proto.send_msg(channel, msg)

