class Sup(Plugin):
    def __init__(self, config={}):
        super(Sup, self).__init__('sup')

    @irc_user_join('traditional dutch greeting')
    def sup(self, user, channel):
        self._proto.send_msg(channel, '%s: sup fucko' % (get_nick(user),))
