import delbert.plugin


class Sup(delbert.plugin.Plugin):
    def __init__(self, config={}):
        super(Sup, self).__init__('sup')

    @delbert.plugin.irc_user_join('traditional dutch greeting')
    def sup(self, user, channel):
        self._proto.send_msg(channel, '%s: sup fucko' % (
            delbert.plugin.get_nick(user),))
