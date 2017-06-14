import random
import string

import delbert.plugin


class Trump(delbert.plugin.Plugin):
    def __init__(self, config={}, seed=None):
        """
        Make a Trumpian comment

        @param config   - configuration.
                            verbosity: probability of commenting
        """
        super(Trump, self).__init__('trump')

        self.verbosity = config.get('verbosity', 0.02)
        self.punctuation = string.maketrans(
                '"#$%&\'()*+,-./:;<=>@[\\]^_`{|}~', 30*" ")
        self.comments = (
            (("?",),
                "I'll keep you in suspense, Ok?"),
            (("she", "her"),
                "Such a nasty woman."),
            (("she", "her"),
                "She would not be my first choice"),
            (("?",),
                "I'm automatically attracted to beautiful"),
            (("russia",),
                "It could be Russia, but it could also be China"),
            (("?",),
                "What the hell do you have to lose?"),
            (("delbert",),
                "I will do my thing that I do very well"),
            (("?",),
                "Why can't we use nuclear weapons?"),
            (("ffs", "jfc"),
                "Get that baby out of here"),
            (("write", "spell", "spelling", "words", "grammar"),
                "They don't know how to write good."),
            (("delbert",),
                "I've made a lot of sacrifices."),
            (("delbert",),
                "I work very, very hard."),
            (("delbert",),
                "I alone can fix it."),
            (("?"),
                "I don't care. It's a long time ago."),
            (("delbert",),
                "I'm much more humble than you would understand."),
            (("why",),
                "Ask the gays what they think."),
            (("why",),
                "There has to be some form of punishment."),
            (("?",),
                "I think you'd have riots."),
            (("why", "?"),
                "All I know is what's on the internet."),
            (("?",),
                "I love the poorly educated."),
            (("",),
                "That was so great."),
            (("bill", "obamacare", "healthcare"),
                'The best thing is to just let it explode.'),
        )

        random.seed(seed)

    def sanitize(self, msg):
        translation = msg.replace("?", " ?")
        translation = translation.replace("!", " !")
        translation = translation.translate(self.punctuation)

        return set(translation.lower().split())

    @delbert.plugin.irc_passive(
        'Offer the best comments. The best. No-one offers better comments.')
    def comment(self, user, channel, msg):
        if(random.random() > self.verbosity):
            return

        def score(words, tags):
            return 10**len(words.intersection(tags))

        # Extract a set of words from the message
        words = self.sanitize(msg)

        # Assign scores to each comment based upon the words in the message
        scores = [score(words, tags) for tags, comment in self.comments]

        # Random selection
        selection = random.random() * sum(scores)

        # Find the matching comment
        for index, score in enumerate(scores):
            selection -= score
            if selection < 0:
                _, comment = self.comments[index]
                self._proto.send_msg(channel, comment)
                break
