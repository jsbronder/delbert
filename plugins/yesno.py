import random

import requests
from twisted.python import log


class YesNo(Plugin):  # noqa: F821
    def __init__(self, config={}):
        super(YesNo, self).__init__('yesno')
        self._config = config
        self._chance = config.get('chance', 0.01)

    def query(self):
        """
        Get an answer

        @return - Tuple of the answer and url to a demostration

        """
        try:
            html = requests.get('http://yesno.wtf/api')
        except requests.exceptions.RequestException, e:
            log.err(str(e))
            return False

        jdict = html.json()
        return (jdict['answer'], jdict['image'])

    @irc_command('query the universe for answers')  # noqa: F821
    def yesno(self, user, channel, args):
        answer, image = self.query()

        msg = '%s! (%s)' % (answer.upper(), image)

        if channel == self.nickname:
            send_to = get_nick(user)  # noqa: F821
        else:
            send_to = channel

        self._proto.send_msg(send_to, msg)

    @irc_passive('Provide answers to the important questions')  # noqa: F821
    def provide_answers(self, user, channel, msg):
        words = msg.strip().split()
        chances = sum(word.endswith('?') for word in words)
        chance = self._chance * chances

        if not chance:
            return

        log.msg('[yesno] %.2f chance to get a response' % (chance,))

        if random.random() <= chance:
            self.yesno(user, channel, '')
