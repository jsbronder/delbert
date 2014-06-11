import requests
from twisted.python import log

class NoDefinition(Exception):
    pass

class UrbanDictionary(Plugin):
    def __init__(self, config={}):
        super(UrbanDictionary, self).__init__('UrbanDictionary')
        self._config = config

    def query(self, term):
        """
        Query urban dictionary for a definition

        @param term - word to lookup on urban dictionary
        @return     - the top definition for the term
        """
        try:
            html = requests.get('http://api.urbandictionary.com/v0/define?term=%s' % (term,))
        except requests.exceptions.RequestException, e:
            log.err(str(e))
            return

        ret = html.json()
        if 'list' in ret and len(ret['list']):
            return ret['list'][0]['definition']
        else:
            raise NoDefinition()

    @irc_command('lookup a term on urban dictionary')
    def ud(self, user, channel, args):
        send_to = get_nick(user) if channel == self.nickname else channel

        if args == '':
            msg = '%s:  someone who does not even know what they want defined' % (
                get_nick(user),)
            self._proto.send_msg(send_to, msg)
        else:
            terms = args.split(' ')
            for term in terms:
                definition = self.query(term)
                self._proto.send_msg(send_to, '%s:  %s' % (
                    term,
                    definition))

