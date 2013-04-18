
def cmd_help(proto, user, channel, args):
    u = user.split('!', 1)[0]
    cmds = proto.factory.commands.keys()
    proto.say(channel, "%s:  Available commands: %s." % (u, ' '.join(cmds)))

def privcmd_help(proto, user, channel, args):
    u = user.split('!', 1)[0]
    cmds = proto.factory.priv_commands.keys()
    proto.msg(user, "%s:  Available commands: %s." % (u, ' '.join(cmds)))


