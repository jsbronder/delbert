import random

from twisted.python import log


class CardsAgainstHumanity(Plugin):  # noqa: F821
    def __init__(self, config={}, seed=None):
        """
        Create a cards against humanity solver.

        @param config   - configuration.
                            white: path to text file with white card lines.
                            black: path to text file with black card lines.
        @param seed     - random seed.

        White file format:
            <answer>

        Black file format:
            <question_intro> @BLANK@ <question_outro>
            <question_intro> ...

        A random white card will be chosen for each @BLANK@ or ... in the black
        card.
        """
        super(CardsAgainstHumanity, self).__init__('cah')
        self._white = None
        self._black = None

        def read_cards(path):
            with open(path) as fp:
                return [
                    l for l in fp.readlines()
                    if not l.startswith('#') and l != '\n']

        try:
            self._black = read_cards(config['black'])
            self._white = read_cards(config['white'])
        except IOError, e:
            log.err('Failed to open db files for cah: %s' % (e,))
            self._have_content = False
        except KeyError, e:
            log.err('Need paths to black and white specified in cah config')
            self._have_content = False
        else:
            self._have_content = True

        if seed is None:
            random.seed()
        else:
            random.seed(seed)

    @property
    def black(self):
        """
        Get a random question
        """
        return random.choice(self._black).strip()

    @property
    def white(self):
        """
        Get a random answer
        """
        return random.choice(self._white).strip().rstrip('.')

    def get_msg(self):
        """
        Match a random black card with the required number of white cards and
        return the mashedup response.
        """
        if self._have_content:
            ret = self.black

            blanks = ret.count('@BLANK@')
            if blanks:
                for _ in range(blanks):
                    ret = ret.replace('@BLANK@', '"%s"' % (self.white,), 1)
            else:
                ret = ret + ' ... ' + self.white
            return ret
        else:
            return 'Install the CAH text files maybe?'

    @irc_command('generate a cards against humanity solution')   # noqa: F821
    def cah(self, user, channel, args):
        nick = get_nick(user)  # noqa: F821
        msg = self.get_msg()

        if channel == self.nickname:
            self._proto.send_msg(nick, msg)
        else:
            self._proto.send_msg(channel, msg)
