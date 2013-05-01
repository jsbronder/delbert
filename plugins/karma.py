import os
import re

import yaml
from twisted.python import log

KARMA_TRACKER = None

class Karma(object):
    def __init__(self):
        self._ds = os.path.join(dbdir, 'karma.yaml')
        self._karma = {}
        self._pos_search = re.compile('(\w+)\+\+(?:\s+|\Z)')
        self._neg_search = re.compile('(\w+)--(?:\s+|\Z)')

        self._refresh()

    def _refresh(self):
        if os.path.exists(self._ds):
            with open(self._ds, 'r') as fp:
                self._karma = yaml.load(fp.read())
                
    def _modify(self, channel, user, amount):
        if not channel in self._karma:
            self._karma[channel] = {}
        if not user in self._karma[channel]:
            self._karma[channel][user] = 0

        self._karma[channel][user] += amount

    def add(self, channel, user):
        self._modify(channel, user, 1)

    def neg(self, channel, user):
        self._modify(channel, user, -1)

    def save(self):
        with open(self._ds, 'w') as fp:
            yaml.dump(self._karma, fp)

    def parse_msg(self, proto, channel, user, msg):
        pos = re.findall(self._pos_search, msg)
        neg = re.findall(self._neg_search, msg)
        save = False

        for nick in pos:
            if nick == user:
                proto.say(channel, "%s: Giving yourself karma?  Lame." % (nick,))
            else:
                self.add(channel, nick)
                log.msg("[%s] Adding karma for %s" % (channel, user,))
                save = True

        for nick in neg:
            if nick == user:
                proto.say(channel, "%s: self loathe much?" % (nick,))
            self.neg(channel, nick)
            log.msg("[%s] Subtracting karma for %s" % (channel, user,))
            save = True

        if save:
            self.save()

    def channel_karma(self, channel):
        if channel in self._karma:
            return self._karma[channel]
        return []

def init():
    global KARMA_TRACKER
    KARMA_TRACKER = Karma()

def passive_karma(proto, channel, user, msg):
    KARMA_TRACKER.parse_msg(proto, channel, get_nick(user), msg)

def cmd_karma(proto, nick, channel, msg):
    karma = KARMA_TRACKER.channel_karma(channel)
    if len(karma):
        proto.notice(channel, 'Karma:')
        for nick, value in karma.items():
            proto.notice(channel, '    %-20s%d' % (nick + ':', value))
    else:
        proto.notice(channel, 'No one in this room has karma, lame.')

def privcmd_karma(proto, nick, channel, msg):
    channels = re.findall('(?:\s|\A)*(#\w+)(?:\s_|\Z)*', msg)
    user = get_nick(nick)

    for channel in channels:
        karma = KARMA_TRACKER.channel_karma(channel)
        if len(karma):
            proto.msg(user, '%s karma:' % (channel,))
            for nick, value in karma.items():
                proto.msg(user, '    %-20s%d' % (nick + ':', value))
        else:
            proto.msg(user, 'No one in %s has karma, lame.' % (channel,))

