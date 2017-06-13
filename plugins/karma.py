import os
import re
import threading

import yaml
from twisted.python import log

KARMA_TRACKER = None


class Karma(Plugin):  # noqa: F821
    def __init__(self, config={}, seed=None):
        super(Karma, self).__init__('karma')
        self._ds = None

        # protects read/write access to the data store
        self._lock = threading.Lock()

        if 'ds' in config:
            opts = 'r'
            if not os.path.exists(config['ds']):
                opts = 'w'

            try:
                open(config['ds'], opts).close()
            except IOError, e:
                log.err('Cannot open data store %s: %s' % (
                    config['ds'],
                    str(e)))
            else:
                self._ds = config['ds']

        self._karma = {}
        self._pos_search = re.compile('(\w+)\+\+(?:\s+|\Z)')
        self._neg_search = re.compile('(\w+)--(?:\s+|\Z)')

        self._refresh()

    def _refresh(self):
        if self._ds is not None:
            with self._lock:
                with open(self._ds, 'r') as fp:
                    self._karma = yaml.load(fp.read())
            if self._karma is None:
                self._karma = {}

    def _modify(self, channel, user, amount):
        if channel not in self._karma:
            self._karma[channel] = {}
        if user not in self._karma[channel]:
            self._karma[channel][user] = 0

        self._karma[channel][user] += amount
        if self._karma[channel][user] == 0:
            del self._karma[channel][user]

    def add(self, channel, thing):
        """
        Add karma in a channel for something.

        @param channel  - channel to add karma in
        @param thing    - thing to add karma for
        """
        self._modify(channel, thing, 1)

    def neg(self, channel, thing):
        """
        Subtract karma in a channel for something.

        @param channel  - channel to subtract karma in
        @param thing    - thing to subtract karma from
        """
        self._modify(channel, thing, -1)

    def save(self):
        """
        Save karma to the data store.
        """
        if self._ds is not None:
            with self._lock:
                with open(self._ds, 'w') as fp:
                    yaml.dump(self._karma, fp)

    def get_karma(self, channel):
        """
        Get the karma dictionary for the specified channel.

        @param channel  - channel to get karma for.
        @return         - mapping of names and karma.
        """
        return self._karma.get(channel, {})

    @irc_passive(  # noqa: F821
        'check messages for X++ or X-- and modify karma for X')
    def passive_karma(self, user, channel, msg):
        user = get_nick(user)  # noqa: F821
        pos = re.findall(self._pos_search, msg)
        neg = re.findall(self._neg_search, msg)
        save = False

        for nick in pos:
            if nick == user:
                self._proto.send_msg(
                    channel,
                    "%s: Giving yourself karma?  Lame." % (nick,))
            else:
                self.add(channel, nick)
                log.msg("[%s] Adding karma for %s from %s" % (
                    channel,
                    nick,
                    user))
                save = True

        for nick in neg:
            if nick == user:
                self._proto.send_msg(
                    channel,
                    "%s: self loathe much?" % (nick,))
            self.neg(channel, nick)
            log.msg("[%s] Subtracting karma for %s from %s" % (
                channel,
                nick,
                user))
            save = True

        if save:
            self.save()

    @irc_command(  # noqa: F821
        'List karma for the current or specified channels')
    def karma(self, user, channel, args):
        channels = args.split(' ')
        if '' in channels:
            channels = [channel]

        if channel == self.nickname:
            send_to = get_nick(user)  # noqa: F821
        else:
            send_to = channel

        for c in channels:
            karma = self.get_karma(c)
            if len(karma):
                self._proto.send_notice(send_to, '%s karma:' % (c,))
                for nick, value in sorted(karma.items(), key=lambda v: v[1]):
                    self._proto.send_notice(
                        send_to,
                        '    %-20s%d' % (nick + ':', value))
            else:
                self._proto.send_msg(
                    send_to,
                    'No one in %s has karma, lame.' % (c,))
