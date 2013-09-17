def user_joined_cmd_sup(proto, channel, user):
    """
    Traditional Dutch greeting.
    """
    nick = get_nick(user)
    if nick == 'ammorrison':
        msg = '%s: getting sick of your shit' % nick
    else:
        msg = '%s: sup fucko' % nick

    proto.say(channel, msg)

