import os
import random
import re

from twisted.python import log

class Source(Plugin):
    def __init__(self, config={}, seed=None):
        """
        Create a referrer to the source.

        @param config   - configuration.
                            url: path the bot source.
                            pre_verbs: list of verbs to match before nickname
                            post_verbs: list of verbs to match after nickname
                            responses: list of responses
        """
        super(Source, self).__init__('source')
        self._source = config.get('url', 'https://github.com/jsbronder/delbert')

        post_verbs = [
            'should',
            'shouldn\'t',
            'needs',
        ]
        pre_verbs = [
            'make',
            'modify',
            'update',
        ]
        self._pre_verbs = config.get('pre_verbs', pre_verbs)
        self._post_verbs = config.get('post_verbs', post_verbs)

        responses = [
            'Put a little effort in jerky',
            'Oh yeah?  Bring it right here',
            'Show me butthole',
            'I bet you could teach me something like that',
            'Sigh',
            'Step up or shut up',
        ]
        self._responses = config.get('responses', responses)

        self._pre_re = None
        self._post_re = None

        if seed:
            random.seed(seed)
        else:
            random.seed()

    def initialize(self, nickname, proto):
        super(Source, self).initialize(nickname, proto)
        pre = '|'.join(self._pre_verbs)
        post = '|'.join(self._post_verbs)
        self._pre_re = re.compile('((%s)\s+)%s(\s+|$)' % (pre, nickname))
        self._post_re = re.compile('(^|\s+)%s(\s+(%s)\s)' % (nickname, post))

    @irc_passive('help user with feature request')
    def request(self, user, channel, msg):
        search = None

        if self._pre_re is not None:
            search = self._pre_re.search(msg)
        if search is None and self._post_re is not None:
            search = self._post_re.search(msg)

        if search is not None:
            to = get_nick(user) if channel == self.nickname else channel
            self._proto.send_msg(
                    to,
                    '%s, %s' % (
                        random.choice(self._responses),
                        self._source))

    @irc_command('show the suggestion box')
    def source(self, user, channel, args):
        to = get_nick(user) if channel == self.nickname else channel
        self._proto.send_msg(to, self._source)
