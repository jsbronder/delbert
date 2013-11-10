import requests
from twisted.python import log


class Github(Plugin):
    def __init__(self, config={}):
        super(Github, self).__init__('github')
        self._config = config

    @property
    def status(self):
        """
        Return current github status.
        """
        try:
            html = requests.get(
                    'https://status.github.com/api/last-message.json',
                    verify=False)
        except requests.exceptions.RequestException, e:
            log.err(str(e))
            return

        if html.json()['status'] == 'good':
            return '%s:  [%s]' % (
                html.json()['created_on'], html.json()['status'])
        else:
            return '%s:  [%s] %s' % (
                html.json()['created_on'], html.json()['status'], html.json()['body'])

    @irc_command('return current github status')
    def github(self, user, channel, args):
        if channel == self.nickname:
            nick = get_nick(user)
            self._proto.send_notice(nick, self.status)
        else:
            self._proto.send_notice(channel, self.status)


