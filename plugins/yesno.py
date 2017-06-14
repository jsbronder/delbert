import random

import requests
from twisted.python import log

import delbert.plugin


class YesNo(delbert.plugin.Plugin):
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

    @delbert.plugin.irc_command('query the universe for answers')
    def yesno(self, user, channel, args):
        answer, image = self.query()
        msg = '%s! (%s)' % (answer.upper(), image)
        self._proto.send_msg(self.send_to(channel, user), msg)

    @delbert.plugin.irc_passive('Provide answers to the important questions')
    def provide_answers(self, user, channel, msg):
        words = msg.strip().split()
        chances = sum(word.endswith('?') for word in words)
        chance = self._chance * chances

        if not chance:
            return

        log.msg('[yesno] %.2f chance to get a response' % (chance,))

        if random.random() <= chance:
            self.yesno(user, channel, '')
