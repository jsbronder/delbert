def user_joined_cmd_sup(bot, channel, user):
    """
    Traditional Dutch greeting.
    """
    msg = '%s: sup fucko' % user
    proto.say(channel, msg)

