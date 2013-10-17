
def cmd_help(proto, user, channel, args):
    u = get_nick(user)
    cmds = proto.factory.channels[channel].cmds
    proto.say(channel, "%s:  Available commands: %s." % (u, ' '.join(cmds)))

def privcmd_help(proto, user, channel, args):
    nick = get_nick(user)
    cmds = proto.factory.channels[channel].cmds
    proto.msg(nick, "Available commands: %s." % (' '.join(cmds),))


