import functools
import getopt
import inspect
import os
import stat
import sys
import time
import types

import yaml

from twisted.words.protocols import irc
from twisted.internet import (
    protocol,
    reactor,
    threads,
)
from twisted.python import log
from twisted.protocols.policies import TrafficLoggingFactory

import channels
import plugin
import utils

DEFAULT_CONFIG = os.path.join(
    os.environ['HOME'], '.config', 'delbert', 'bot.conf')

class BotProtocol(irc.IRCClient):
    lineRate = 0.5

    def __init__(self, nickname, pw, channels):
        """
        Create an irc bot.

        @param nickname - nickname of the bot.
        @param pw       - password for the bot.
        @param channels - list of channels the bot should join.
        """
        self._nickname = nickname
        self._pw = pw
        self._channels = channels
        self._command_char = '!'

    @property
    def nickname(self):
        """
        Bot nickname
        """
        return self._nickname

    def _log_callback(self, *args, **kwds):
        if hasattr(args[1], 'printTraceback'):
            args[1].printTraceback()
        log.msg(args[0], system=kwds['system'] if 'system' in kwds else 'BotProtocol')

    def signedOn(self):
        log.msg("Signed on")
        self.msg('nickserv', 'identify %s %s' % (self._nickname, self._pw))
        for channel in [c for c in self._channels.keys() if not c == self._nickname]:
            self.join(channel)

    def send_msg(self, target, msg):
        """
        Send a message to a user or a channel

        @param target   - user or channel to send a message to.
        @param msg      - message to send.
        """
        if isinstance(msg, types.UnicodeType):
            msg = msg.encode('utf-8')
        self.msg(target, msg)

    def send_notice(self, channel, msg):
        """
        Send a notice to a user or a channel

        @param target   - user or channel to send a notice to.
        @param msg      - notice to send.
        """
        if isinstance(msg, types.UnicodeType):
            msg = msg.encode('utf-8')
        self.notice(channel, msg)

    def _call(self, *args, **kwds):
        """
        Defer a method to a thread.  All arguments and keywords are passed
        to the method aside from the following:

        Keywords:
            @param cb   - callback when method finishes with success.
            @param eb   - callback when method finishes with error.
        """
        cb = kwds.pop('cb', None)
        eb = kwds.pop('eb', None)

        th = threads.deferToThread(*args, **kwds)

        if cb is not None:
            th.addCallback(cb)

        if eb is not None:
            th.addErrback(eb)

    def joined(self, channel):
        log.msg("Joined %s" % (channel,))

    def userJoined(self, user, channel):
        log.msg('%s joined %s' % (user, channel))

        nick = utils.get_nick(user)

        for name, f in self._channels[channel].user_joins.items():
            eb = functools.partial(self._log_callback, '<%s> error' % (name,), system=channel)
            self._call(f, nick, channel, eb=eb)

    def privmsg(self, user, channel, msg):
        if not channel in self._channels:
            return

        if msg.startswith(self._command_char):
            cmd = msg[1:]
            try:
                cmd, args = cmd.split(' ', 1)
            except ValueError:
                args = '' 

            if cmd == 'help':
                self._help(channel, args)
            elif cmd == 'passives':
                self._help(channel, args, 'passives')
            elif cmd == 'user_joins':
                self._help(channel, args, 'user_joins')
            else:
                self._cmd(user, channel, cmd, args)

        elif not channel == self._nickname:
            for name, f in self._channels[channel].passives.items():
                eb = functools.partial(
                        self._log_callback,
                        'passive %s failed' % (name,),
                        system=channel)
                self._call(f, user, channel, msg, eb=eb)

    def _cmd(self, user, channel, cmd, args):
        """
        Respond to an irc command.

        @param user     - user calling command.
        @param channel  - channel user is calling command from.
        @param args     - command arguments.
        """
        f = self._channels[channel].commands.get(cmd, None)
        if f is not None:
            cb = functools.partial(self._log_callback, '!%s completed' % (cmd,), system=channel)
            eb = functools.partial(self._log_callback, '!%s error' % (cmd,), system=channel)
            self._call(f, user, channel, args, cb=cb, eb=eb)

    def _help(self, channel, search, type='commands'):
        """
        Respond to the 'help' command.

        Checks the list of commands registered for this channel and returns
        the help text for each command if it starts with the search parameter.

        @param channel  - channel in which help was called.
        @param search   - command to search for.  If an empty string then every
                          registered command will be listed.
        @param type     - type of command to get help for.  Valid types are
                          commands, passives or user_joins.
        """
        search = search.split(' ')[0]
        mapping = getattr(self._channels[channel], type, {})
        names = sorted(mapping.keys())
        for name in [n for n in names if n.startswith(search)]:
            self.send_notice(channel, '%s:  %s' % (name, mapping[name].help))

class BotFactory(protocol.ClientFactory):
    def __init__(self, config):
        self._config = config
        self.nickname = config['nick']
        self.pw = config['pass']
        self.dbdir = config['dbdir']

        self.channels = {
            self.nickname: channels.Channel(self.nickname, {
                'load_passives': False,
                'load_user_joins': False}),
        }

        for channel, config in config['channels'].items():
            self.channels[channel] = channels.Channel(
                    channel,
                    config if config is not None else {})

        self._plugins = []
        self._load_plugins()

    def buildProtocol(self, address):
        proto = BotProtocol(self.nickname, self.pw, self.channels)
        _ = [p.initialize(self.nickname, proto) for p in self._plugins]
        return proto

    def clientConnectionLost(self, connector, reason):
        log.err("Lost connection: %s" % (reason,))
        time.sleep(1)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        log.err("Connection failed: %s" % (reason,))
        time.sleep(1)
        connector.connect()

    def _get_plugin_env(self):
        return {
            'get_nick': utils.get_nick,
            'get_host': utils.get_host,
            'dbdir': self.dbdir,
            'Plugin': plugin.Plugin,
            'irc_command': plugin.irc_command,
            'irc_passive': plugin.irc_passive,
            'irc_user_join': plugin.irc_user_join,
        }

    def _load_plugins(self, path = 'plugins'):
        def is_plugin(obj):
            return (type(obj) == type
                and obj != plugin.Plugin
                and plugin.Plugin in inspect.getmro(obj))

        for pfile in os.listdir(path):
            if pfile.endswith('.py') and not pfile.startswith('__'):
                pname = pfile[:-3]

                try:
                    env = self._get_plugin_env()
                    execfile(os.path.join(path, pfile), env)

                except ImportError, e:
                    log.err("Failed to log plugin '%s': %s" % (pname, e))
                    continue

                for obj in [obj for obj in env.values() if is_plugin(obj)]:
                    log.msg("Loaded %s.%s" % (pname, obj.__name__))
                    self._plugins.append(obj(self._config.get(pname, {})))

        for channel in self.channels.values():
            _ = [channel.register_plugin(p) for p in self._plugins]


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
        opts, args = getopt.getopt(sys.argv[1:], 'hc:t:',
            ['help', 'config=', 'traffic='])
    except getopt.GetoptError, e:
        print (str(e))
        sys.exit(1)

    config_path = DEFAULT_CONFIG
    traffic_log = None

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

    if traffic_log is not None:
        lf = TrafficLoggingFactory(bot, traffic_log)
        reactor.connectTCP(config['server'], config['port'], lf)
    else:
        reactor.connectTCP(config['server'], config['port'], bot)

    reactor.run()


if __name__ == "__main__":
    main()

