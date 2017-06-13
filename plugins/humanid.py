import requests
from twisted.python import log


class HumanId(Plugin):  # noqa: F821
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

    @irc_command(  # noqa: F821
        'get a potentially funny human readable unique id')
    def humanid(self, user, channel, args):
        if channel == self.nickname:
            dest = get_nick(user)  # noqa: F821
        else:
            dest = channel
        self._proto.send_msg(dest, self.get_some())
