class Sup(Plugin):  # noqa: F821
    def __init__(self, config={}):
        super(Sup, self).__init__('sup')

    @irc_user_join('traditional dutch greeting')  # noqa: F821
    def sup(self, user, channel):
        self._proto.send_msg(channel, '%s: sup fucko' % (
            get_nick(user),))  # noqa: F821
