
def cmd_help(proto, user, channel, args):
    u = user.split('!', 1)[0]
    cmds = proto.factory.commands.keys()
    proto.say(channel, "%s:  Available commands: %s." % (u, ' '.join(cmds)))


