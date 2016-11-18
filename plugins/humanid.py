import requests
from twisted.python import log

class HumanId(Plugin):
    def __init__(self, config={}):
        super(HumanId, self).__init__('HumanId')
        self._config = config

    def get_some(self):
        """
        get a human id
        @return     - a human readable 'unique' id
        """
        html = requests.get('https://uz83qtfqh2.execute-api.us-east-1.amazonaws.com/dev')
        try:
            html = requests.get('https://uz83qtfqh2.execute-api.us-east-1.amazonaws.com/dev')
        except requests.exceptions.RequestException, e:
            log.err(str(e))
            return

        return html.json().get('text', 'got nothing')

    @irc_command('get a potentially funny human readable unique id')
    def humanid(self, user, channel, args):
        send_to = get_nick(user) if channel == self.nickname else channel
        self._proto.send_msg(send_to, self.get_some())


