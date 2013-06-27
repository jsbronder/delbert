import os
import random

INSTANCE = None

class CardsAgainstHumanity(object):
    def __init__(self):
        try:
            with open(os.path.join(dbdir, 'cah-white.txt')) as fp:
                self._white = [l for l in fp.readlines() if not l.startswith('#') and l != '\n']

            with open(os.path.join(dbdir, 'cah-black.txt')) as fp:
                self._black = [l for l in fp.readlines() if not l.startswith('#') and l != '\n']

        except IOError:
            self._have_content = False
        else:
            self._have_content = True

        random.seed()

    @property
    def black(self):
        return random.choice(self._black).strip()

    @property
    def white(self):
        return random.choice(self._white).strip().rstrip('.')

    @property
    def have_content(self):
        return self._have_content

    def msg(self):
        if self.have_content:
            ret = self.black

            blanks = ret.count('@BLANK@')
            if blanks:
                for _ in range(blanks):
                    ret = ret.replace('@BLANK@', '"%s"' % (self.white,), 1)
            else:
                ret = ret + ' ... ' + self.white
            return ret
        else:
            return 'What did someone forget to do?  ...  Install the CAH text files.'

def init():
    global INSTANCE
    INSTANCE = CardsAgainstHumanity()

def cmd_cah(proto, _, channel, __):
    proto.msg(channel, INSTANCE.msg())

