import random

import yaml

from twisted.python import log

import delbert.plugin


class SprintGoals(delbert.plugin.Plugin):
    def __init__(self, config={}, seed=None):
        super(SprintGoals, self).__init__('sprint')

        try:
            with open(config['sprint']) as fp:
                data = yaml.load(fp)
                self.nouns = data['nouns']
                self.verbs = data['verbs']
                self.adverbs = data['adverbs']
                self.adjectives = data['adjectives']

        except IOError, e:
            log.err('Failed to open db file for SprintGoals: %s' % (e,))
            self._have_content = False
        except KeyError, e:
            log.err('Need path to SprintGoals config')
            self._have_content = False
        else:
            self._have_content = True

        if seed is None:
            random.seed()
        else:
            random.seed(seed)

    def get_msg(self):
        if self._have_content:
            return "{adverb} {verb} {adjective} {noun}".format(
                    adjective=random.choice(self.adjectives),
                    adverb=random.choice(self.adverbs),
                    verb=random.choice(self.verbs),
                    noun=random.choice(self.nouns))
        else:
            return 'Install the SPRINT text files maybe?'

    @delbert.plugin.irc_command('generate a sprint goal')
    def sprint(self, user, channel, args):
        msg = self.get_msg()
        self._proto.send_msg(self.send_to(channel, user), msg)
