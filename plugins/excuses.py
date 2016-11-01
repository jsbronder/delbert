from bs4 import BeautifulSoup as soup
import requests
from twisted.python import log

class Excuses(Plugin):
    def __init__(self, config={}):
        super(Excuses, self).__init__('Excuses')
        self._config = config

    def query_excuse(self):
        """
        Query the excuse generator.

        @return  -  why the code is broken/incomplete/not-finished/unexpected/you_getThe-idea
                    None if parsing failed.
        """
        try:
            html = requests.get('http://developerexcuses.com', verify=False)
        except requests.exceptions.RequestException, e:
            log.err(str(e))
            return

        parsed = soup(html.text, 'html.parser')
        return parsed.a.text

    @irc_command('generate an excuse for why the code is broken/incomplete/failing/holding the president for ransom')
    def excuse(self, user, channel, args):
        msg = self.query_excuse()

        if channel == self.nickname:
            self._proto.send_msg(get_nick(user), msg)
        else:
            self._proto.send_msg(channel, msg)

