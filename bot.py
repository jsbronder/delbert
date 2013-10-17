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
)
from twisted.python import log
from twisted.protocols.policies import TrafficLoggingFactory

import channels
import utils

DEFAULT_CONFIG = os.path.join(
    os.environ['HOME'], '.config', 'delbert', 'bot.conf')

class BotProtocol(irc.IRCClient):
    lineRate = 0.5

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
        for channel in [c for c in self.factory.channels.keys() if not c == self.nickname]:
            self.join(channel)

    def joined(self, channel):
        log.msg("Joined %s" % (channel,))

    def userJoined(self, user, channel):
        log.msg('%s joined %s' % (user, channel))
        self.factory.channels[channel].handle_join(self, user)

    def privmsg(self, user, channel, msg):
        self.factory.channels[channel].handle_msg(self, user, msg)

class BotFactory(protocol.ClientFactory):
    protocol = BotProtocol

    def __init__(self, config):
        self.command_char = '!'
        self._config = config
        self.nickname = config['nick']
        self.pw = config['pass']
        self.dbdir = config['dbdir']

        self.channels = {
            self.nickname: channels.Channel(self.nickname, self.command_char),
        }
        self.channels.update({name: channels.Channel(name, self.command_char)
                for name in config['channels'].keys()})

        self.plugins = []
        self.commands = {}
        self.priv_commands = {}
        self.user_joined = {}
        self.passive = {}


        self._load_plugins(config['channels'])

    def clientConnectionLost(self, connector, reason):
        log.err("Lost connection: %s" % (reason,))
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        log.err("Connection failed: %s" % (reason,))
        reactor.stop()

    def _get_plugin_env(self, plugin_name):
        return {
            'get_nick': utils.get_nick,
            'get_host': utils.get_host,
            'dbdir': self.dbdir,
            'config': self._config.get(plugin_name, {})
        }

    def _load_plugins(self, channel_config, path = 'plugins'):
        plugins = {}

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

                plugins[pname] = {
                    'cmds': [],
                    'passive': [],
                    'user_join': [],
                    'privcmds': [],
                }

                for name, obj in env.items():
                    if type(obj) != types.FunctionType:
                        continue

                    elif name == 'init':
                        obj()

                    elif name.startswith('cmd_'):
                        plugins[pname]['cmds'].append((name[4:], obj))

                    elif name.startswith('passive_'):
                        plugins[pname]['passive'].append((name[8:], obj))

                    elif name.startswith('user_joined_cmd_'):
                        plugins[pname]['user_join'].append((name[16:], obj))

                    elif name.startswith('privcmd_'):
                        plugins[pname]['privcmds'].append((name[8:], obj))

        for channel in self.channels.values():
            for plugin, objs in plugins.items():
                if (channel.name != self.nickname
                        and not plugin in channel_config[channel.name]['plugins']):
                    continue

                if channel.name != self.nickname:
                    for name, obj in objs['cmds']:
                        channel.register_cmd(name, obj)

                    for name, obj in objs['passive']:
                        channel.register_passive(name, obj)

                    for name, obj in objs['user_join']:
                        channel.register_user_join(name, obj)
                else:
                    for name, obj in objs['privcmds']:
                        channel.register_cmd(name, obj)


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

