import requests
from twisted.python import log

import delbert.plugin


class IsItDown(delbert.plugin.Plugin):
    def __init__(self, config={}):
        super(IsItDown, self).__init__('isitdown')
        self._config = config

    @staticmethod
    def parse_site(url):
        """
        Strip the protocol and any path from a URL leaving only the site.

        @param url  - url to strip
        @return     - site contained within the url
        """
        site = url.strip()

        if '://' in site:
            site = site[site.find('://') + 3:]

        if '/' in site:
            site = site[:site.find('/')]

        return site

    def query(self, url):
        """
        Query the site checker

        @return  - True if the site is up, False otherwise.
        """
        try:
            html = requests.get(
                    'http://downforeveryoneorjustme.com/%s' % (url,),
                    verify=False)
        except requests.exceptions.RequestException, e:
            log.err(str(e))
            return False

        return 'not just you!' not in html.text

    @delbert.plugin.irc_command(
        'check if a site or sites are down for everyone')
    def isitdown(self, user, channel, args):
        send_to = self.send_to(channel, user)

        if len(args):
            urls = args.split(' ')

            for url in urls:
                site = self.parse_site(url)

                up = self.query(site)
                msg = '%s is %s' % (site, 'up' if up else 'down')

                self._proto.send_msg(send_to, msg)
        else:
            msg = 'Check if what site or sites are down for everyone?'
            self._proto.send_msg(send_to, msg)
