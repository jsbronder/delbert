def user_joined_cmd_sup(proto, channel, user):
    """
    Traditional Dutch greeting.
    """
    msg = '%s: sup fucko' % proto.factory.get_nick(user)
    proto.say(channel, msg)

