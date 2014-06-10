import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'delbert')))

import bot
import channels
import plugin
import utils

plugin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../plugins'))

TEST_CHANNEL = '#test'
TEST_NICK = 'testbot'

def load_plugin(name, obj_name, config={}, *args, **kwds):
    env = {
        'get_nick': utils.get_nick,
        'get_host': utils.get_host,
        'dbdir': '/tmp/',
        'Plugin': plugin.Plugin,
        'irc_command': plugin.irc_command,
        'irc_passive': plugin.irc_passive,
        'irc_user_join': plugin.irc_user_join,
    }

    execfile(os.path.join(plugin_dir, name), env)
    return env[obj_name](config, *args, **kwds)

class TestProto(bot.BotProtocol):
    def __init__(self, plugins):
        priv_channel = channels.Channel(TEST_NICK, {})
        _ = [priv_channel.register_plugin(p) for p in plugins]

        channel_map = {
            TEST_CHANNEL: TestChannel(plugins),
            TEST_NICK: priv_channel,
        }
        _ = [p.initialize(TEST_NICK, self) for p in plugins]
        self._msgs = []
        bot.BotProtocol.__init__(self, TEST_NICK, 'pw', channel_map)

    @property
    def msgs(self):
        return self._msgs

    def clear(self):
        self._msgs = []

    def _call(self, *args, **kwds):
        _ = kwds.pop('cb', None)
        _ = kwds.pop('eb', None)

        args[0](*args[1:], **kwds)

    def send_msg(self, channel, msg):
        self._msgs.append(('msg', channel, msg))

    def send_notice(self, channel, msg):
        self._msgs.append(('notice', channel, msg))

class TestChannel(channels.Channel):
    def __init__(self, plugins):
        config = {
            'config-plugin': {
                'commands': ['cmd1'],
            },
        }
        super(TestChannel, self).__init__(TEST_CHANNEL, config)
        _ = [self.register_plugin(p) for p in plugins]


