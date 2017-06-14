import urllib

import requests
from twisted.python import log

import delbert.plugin


class NoDefinition(Exception):
    pass


class UrbanDictionary(delbert.plugin.Plugin):
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
            html = requests.get(
                'http://api.urbandictionary.com/v0/define?term=%s' % (term,))
        except requests.exceptions.RequestException, e:
            log.err(str(e))
            return

        ret = html.json()
        if 'list' in ret and len(ret['list']):
            return ret['list'][0]['definition']
        else:
            raise NoDefinition()

    @delbert.plugin.irc_command('lookup a term on urban dictionary')
    def ud(self, user, channel, args):
        if channel == self.nickname:
            send_to = delbert.plugin.get_nick(user)
        else:
            send_to = channel

        if args == '':
            msg = "%s:  someone who doesn't know what they want defined" % (
                delbert.plugin.get_nick(user),)
            self._proto.send_msg(send_to, msg)
        else:
            terms = '+'.join(urllib.quote(t) for t in args.split())
            try:
                definition = self.query(terms)
                self._proto.send_msg(send_to, '%s:  %s' % (
                    args,
                    definition))
            except NoDefinition:
                self._proto.send_msg(send_to, "No idea :(")
