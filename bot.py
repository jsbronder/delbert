import getopt
import os
import stat
import sys
import types

import yaml

from twisted.words.protocols import irc
from twisted.internet import (
    protocol,
    reactor,
    threads)
from twisted.python import log
from twisted.protocols.policies import TrafficLoggingFactory

DEFAULT_CONFIG = os.path.join(
    os.environ['HOME'], '.config', 'delbert', 'bot.conf')

class BotProtocol(irc.IRCClient):
    @property
    def nickname(self):
        return self.factory.nickname

    def _log_callback(self, *args, **kwds):
        if hasattr(args[0], 'printTraceback'):
            args[0].printTraceback()
        log.msg(args[1], system='BotProtocol')

    def signedOn(self):
        log.msg("Signed on")
        self.msg('nickserv', 'identify %s %s' %
            (self.factory.nickname, self.factory.pw))
        for channel in self.factory.channels:
            self.join(channel)

    def joined(self, channel):
        log.msg("Joined %s" % (channel,))

    def userJoined(self, user, channel):
        log.msg("%s joined %s", (user, channel))
        for name, funcs in self.factory.user_joined.items():
            for func in funcs:
                th = threads.deferToThread(func, self, channel, user)
                th.addErrback(self._log_callback, '<%s> error' % (name,))

    def privmsg(self, user, channel, msg):
        if msg.startswith(self.factory.command_char):
            self._cmd(user, channel, msg[1:])
        elif channel != self.nickname:
            for name, funcs in self.factory.passive.items():
                for func in funcs:
                    th = threads.deferToThread(func, self, channel, user, msg)
                    th.addErrback(self._log_callback, '<%s> error' % (name,))

    def _cmd(self, user, channel, cmd):
        try:
            cmd, args = cmd.split(" ", 1)
        except ValueError:
            args = ""

        nick = self.factory.get_nick(user)

        if channel != self.nickname:
            for mod in self.factory.commands.get(cmd, []):
                log.msg("[%s] %s called %s %s" % (channel, nick, cmd, args))
                th = threads.deferToThread(mod, self, user, channel, args)
                th.addCallback(self._log_callback, '<%s> completed' % (cmd,))
                th.addErrback(self._log_callback, '<%s> error' % (cmd,))
        else:
            for mod in self.factory.priv_commands.get(cmd, []):
                log.msg("[%s] %s called %s %s" % (channel, nick, cmd, args))
                th = threads.deferToThread(mod, self, user, channel, args)
                th.addCallback(self._log_callback, '<%s> completed' % (cmd,))
                th.addErrback(self._log_callback, '<%s> error' % (cmd,))

class BotFactory(protocol.ClientFactory):
    protocol = BotProtocol

    def __init__(self, config):
        self._config = config
        self.channels = config['channels']
        self.nickname = config['nick']
        self.pw = config['pass']
        self.dbdir = config['dbdir']

        self.plugins = []
        self.commands = {}
        self.priv_commands = {}
        self.user_joined = {}
        self.passive = {}

        self.command_char = '!'

        self._load_plugins()

    @staticmethod
    def get_nick(full_name):
        return full_name.split('!', 1)[0]

    @staticmethod
    def get_host(full_name):
        return str(full_name).strip().split('@', 1)[1]

    def clientConnectionLost(self, connector, reason):
        log.err("Lost connection: %s" % (reason,))
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        log.err("Connection failed: %s" % (reason,))
        reactor.stop()

    def _get_plugin_env(self, plugin_name):
        return {
            'get_nick': self.get_nick,
            'get_host': self.get_host,
            'dbdir': self.dbdir,
            'config': self._config.get(plugin_name, {})
        }

    def _load_plugins(self, path = 'plugins'):
        for pfile in os.listdir(path):
            if pfile.endswith('.py') and not pfile.startswith('__'):
                pname = pfile[:-3]
                try:
                    env = self._get_plugin_env(pname)
                    execfile(os.path.join(path, pfile), env)

                except ImportError, e:
                    log.err("Failed to log plugin '%s': %s" % (pname, e))
                    continue
                else:
                    log.msg("Loaded plugin '%s'" % (pname,))

                self.plugins.append(env)

                for name, obj in env.items():
                    if type(obj) != types.FunctionType:
                        continue

                    elif name == 'init':
                        obj()

                    elif name.startswith('cmd_'):
                        cmd = name[4:]
                        if not cmd in self.commands.keys():
                            self.commands[cmd] = []
                        self.commands[cmd].append(obj)

                    elif name.startswith('privcmd_'):
                        cmd = name[8:]
                        if not cmd in self.priv_commands.keys():
                            self.priv_commands[cmd] = []
                        self.priv_commands[cmd].append(obj)

                    elif name.startswith('passive_'):
                        cmd = name[8:]
                        if not cmd in self.passive:
                            self.passive[cmd] = []
                        self.passive[cmd].append(obj)

                    elif name.startswith('user_joined_cmd_'):
                        cmd = name[16:]
                        self.user_joined[cmd].append(obj)

        log.msg('Commands: %s' % (' '.join(self.commands.keys())))
        log.msg('Priv Commands: %s' % (' '.join(self.priv_commands.keys())))
        log.msg('Passive Commands: %s' % (' '.join(self.passive.keys())))
        log.msg('User Joined Commands: %s' % (' '.join(self.user_joined.keys())))

def parse_config(path):
    perms = stat.S_IMODE(os.stat(path).st_mode)
    if perms & stat.S_IRGRP or perms & stat.S_IROTH:
        print("Warning:  unsafe config permissions")

    with open(path) as f:
        config = yaml.load(f.read())

    missing = []
    for key in ('server', 'port', 'nick', 'pass'):
        if not key in config:
            missing.append(key)

    if len(missing):
        raise KeyError("Missing required configuration keys: %s"
            % ' '.join(missing))

    if 'dbdir' in config:
        config['dbdir'] = os.path.expanduser(config['dbdir'])
        if not config['dbdir'].startswith('/'):
            config['dbdir'] = os.path.join(os.path.dirname(path), config['dbdir'])
    else:
        config['dbdir'] = os.path.join(os.path.dirname(path), 'db')

    if not os.path.exists(config['dbdir']):
        os.makedirs(config['dbdir'])
    elif not os.path.isdir(config['dbdir']):
        raise OSError("dbdir '%s' exists but is not a directory" %
            (config['dbdir'],))

    return config

def usage():
    print """%s [ARGUMENTS]

ARGUMENTS:
    -h, --help              This screen
    -c, --config [FILE]     Path to config file [%s]
    -t, --traffic [FILE]    Log traffic to specified file
"""

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hc:', ['help', 'config='])
    except getopt.GetoptError, e:
        print (str(e))
        sys.exit(1)

    config_path = DEFAULT_CONFIG
    traffic_log = False

    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif o in ('-c', '--config'):
            config_path = a
        elif o in ('-t', '--traffic'):
            traffic_log = a

    config = parse_config(config_path)

    if 'logfile' in config:
        if config['logfile'] == 'stdout':
            log.startLogging(sys.stdout)
        else:
            log.startLogging(config['logfile'])

    bot = BotFactory(config)

    if traffic_log:
        lf = TrafficLoggingFactory(bot, 'irc')
        reactor.connectTCP(config['server'], config['port'], lf)
    else:
        reactor.connectTCP(config['server'], config['port'], bot)

    reactor.run()


if __name__ == "__main__":
    main()

