import netrc
import os
import sys
import types

from twisted.words.protocols import irc
from twisted.internet import (
    protocol,
    reactor,
    threads)
from twisted.python import log

class BotProtocol(irc.IRCClient):
    @property
    def nickname(self):
        return self.factory.nickname

    def _log_callback(self, *args, **kwds):
        log.msg(args[1], system='BotProtocol')

    def signedOn(self):
        log.msg("Signed on")
        self.join(self.factory.channel)
        self.msg('nickserv', 'identify %s %s' %
            (self.factory.nickname, self.factory.pw))

    def joined(self, channel):
        log.msg("Joined %s" % (channel,))

    def privmsg(self, user, channel, msg):
        log.msg("[%s] <%s>:  %s" % (channel, user, msg))
        if msg.startswith(self.factory.command_char):
            self._cmd(user, channel, msg[1:])

    def _cmd(self, user, channel, cmd):
        try:
            cmd, args = cmd.split(" ", 1)
        except ValueError:
            args = ""

        nick = self.factory.get_nick(user)
        for mod in self.factory.commands.get(cmd, []):
            log.msg("[%s] %s called %s %s" % (channel, nick, cmd, ' '.join(args)))
            th = threads.deferToThread(mod, self, nick, channel, args)
            th.addCallback(self._log_callback, '<%s> completed' % (cmd,))
            th.addErrback(self._log_callback, '<%s> error' % (cmd,))

class BotFactory(protocol.ClientFactory):
    protocol = BotProtocol

    def __init__(self, channel, nickname, pw):
        self.channel = channel
        self.nickname = nickname
        self.pw = pw
        self.plugins = []
        self.commands = {}

        self.command_char = '!'

        self._load_plugins()

    @staticmethod
    def get_nick(full_name):
        return full_name.split('!', 1)[0]

    def clientConnectionLost(self, connector, reason):
        log.err("Lost connection: %s" % (reason,))
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        log.err("Connection failed: %s" % (reason,))
        reactor.stop()

    def _get_plugin_env(self):
        return {
            'get_nick': self.get_nick,
        }

    def _load_plugins(self, path = 'plugins'):
        for pfile in os.listdir(path):
            if pfile.endswith('.py') and not pfile.startswith('__'):
                pname = pfile[:-3]
                try:
                    env = self._get_plugin_env()
                    execfile(os.path.join(path, pfile), env)

                except ImportError, e:
                    log.err("Failed to log plugin '%s': %s" % (pname, e))
                    continue
                else:
                    log.msg("Loaded plugin '%s'" % (pname,))

                self.plugins.append(env)

                for name, obj in env.items():
                    if name.startswith('cmd_') and type(obj) == types.FunctionType:
                        cmd = name[4:]
                        if not cmd in self.commands.keys():
                            self.commands[cmd] = []
                        self.commands[cmd].append(obj)

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    auth = netrc.netrc().authenticators('irc.freenode.net')
    if not len(auth):
        log.err("No authentication for irc.freenode.net in ~/.netrc")
        sys.exit(1)

    b = BotFactory('#delbert-test', auth[0], auth[2])
    from twisted.protocols.policies import TrafficLoggingFactory
    lf = TrafficLoggingFactory(b, 'irc')
    reactor.connectTCP('irc.freenode.net', 6667, lf)

    reactor.run()
