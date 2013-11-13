import os
import sys
import unittest

import base

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bot
import channels
import plugin
import utils

class TestPlugin(plugin.Plugin):
    def __init__(self):
        super(TestPlugin, self).__init__('test-plugin')

    @plugin.irc_command('say_f help')
    def say_f(self, user, channel, args):
        if channel == self.nickname:
            self._proto.send_msg(utils.get_nick(user), 'secret f')
        else:
            self._proto.send_msg(channel, 'f')

    @plugin.irc_command('say_g help')
    def say_g(self, user, channel, args):
        if channel == self.nickname:
            self._proto.send_msg(utils.get_nick(user), 'secret g')
        else:
            self._proto.send_msg(channel, 'g')

    @plugin.irc_command('notice_f help')
    def notice_f(self, user, channel, args):
        self._proto.send_notice(channel, 'f')

    @plugin.irc_user_join('user_join_f help')
    def user_join_f(self, user, channel):
        self._proto.send_msg(channel, 'hi %s' % (user,))

    @plugin.irc_passive('passive command')
    def hammer(self, user, channel, msg):
        if msg.endswith(' stop'):
            self._proto.send_msg(channel, 'hammertime')

class ConfigPlugin(plugin.Plugin):
    def __init__(self):
        super(ConfigPlugin, self).__init__('config-plugin')

    @plugin.irc_command('cmd1 help')
    def cmd1(self, user, channel, args):
        self._proto.send_msg(channel, 'cmd1')

    @plugin.irc_command('cmd2 help')
    def cmd2(self, user, channel, args):
        self._proto.send_msg(channel, 'cmd2')


class PluginTester(unittest.TestCase):
    def setUp(self):
        plugins = [TestPlugin(), ConfigPlugin()]
        self._proto = base.TestProto(plugins)

    def test_cmd(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!say_f')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('msg', base.TEST_CHANNEL, 'f'))

    def test_notice(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!notice_f')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('notice', base.TEST_CHANNEL, 'f'))

    def test_user_join(self):
        self._proto.userJoined('tester', base.TEST_CHANNEL)
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('msg', base.TEST_CHANNEL, 'hi tester'))

    def test_ignore_channel(self):
        self._proto.privmsg('tester', '#test-ignore', '!say_f')
        self.assertEqual(0, len(self._proto.msgs))

    def test_help_f(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!help say_f')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('notice', base.TEST_CHANNEL, 'say_f:  say_f help'))

    def test_help(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!help')
        self.assertEqual(4, len(self._proto.msgs))
        self.assertEqual(
                self._proto.msgs,
                [
                    ('notice', base.TEST_CHANNEL, 'cmd1:  cmd1 help'),
                    ('notice', base.TEST_CHANNEL, 'notice_f:  notice_f help'),
                    ('notice', base.TEST_CHANNEL, 'say_f:  say_f help'),
                    ('notice', base.TEST_CHANNEL, 'say_g:  say_g help'),
                ],)

    def test_help2(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!help say')
        self.assertEqual(2, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs,
                [
                    ('notice', base.TEST_CHANNEL, 'say_f:  say_f help'),
                    ('notice', base.TEST_CHANNEL, 'say_g:  say_g help'),
                ],)

    def test_help_passives(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!passives')
        self.assertEqual(
                self._proto.msgs,
                [('notice', base.TEST_CHANNEL, 'hammer:  passive command')],)

    def test_help_user_joins(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!user_joins')
        self.assertEqual(
                self._proto.msgs,
                [('notice', base.TEST_CHANNEL, 'user_join_f:  user_join_f help')],)

    def test_passive_f(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, 'blah blah blah')
        self.assertEqual(0, len(self._proto.msgs))

        self._proto.privmsg('tester', base.TEST_CHANNEL, 'Sometimes I just want to stop')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('msg', base.TEST_CHANNEL, 'hammertime'))

    def test_config_whitelist(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!cmd2')
        self.assertEqual(0, len(self._proto.msgs))

        self._proto.privmsg('tester', base.TEST_CHANNEL, '!cmd1')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('msg', base.TEST_CHANNEL, 'cmd1'))

    def test_privchannel(self):
        self._proto.privmsg('tester', base.TEST_NICK, '!say_f')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0], ('msg', 'tester', 'secret f'))


def main():
    unittest.main()

if __name__ == '__main__':
    main()
