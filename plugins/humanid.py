import requests
from twisted.python import log

import delbert.plugin


class HumanId(delbert.plugin.Plugin):
    def __init__(self, config={}):
        super(HumanId, self).__init__('HumanId')
        self._config = config

    def get_some(self):
        """
        get a human id
        @return     - a human readable 'unique' id
        """
        try:
            html = requests.get(
                'https://uz83qtfqh2.execute-api.us-east-1.amazonaws.com/dev')
        except requests.exceptions.RequestException, e:
            log.err(str(e))
            return

        return html.json().get('text', 'got nothing')

    @delbert.plugin.irc_command(
        'get a potentially funny human readable unique id')
    def humanid(self, user, channel, args):
        self._proto.send_msg(self.send_to(channel, user), self.get_some())
