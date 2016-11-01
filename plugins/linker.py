import re

import requests
import requests_oauthlib
from twisted.python import log
from bs4 import BeautifulSoup as soup

twitter_auth = None

class Linker(Plugin):
    def __init__(self, config):
        super(Linker, self).__init__('linker')
        self._config = config
        self._twitter_auth = None
        self._url_re = re.compile(
            'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self._twitter_re = re.compile(
            'http[s]?://(?:www.)?twitter.com/.+/status/([0-9]+)')

        self._setup_twitter()

    def _setup_twitter(self):
        need = ['app_key', 'app_secret', 'user_token', 'user_secret']
        for n in need:
            if not n in self._config:
                return

        try:
            self._twitter_auth = requests_oauthlib.OAuth1(
                    self._config['app_key'],
                    self._config['app_secret'],
                    self._config['user_token'],
                    self._config['user_secret'])
        except Exception, e:
            log.err("Couldn't authenticate with twitter: %s " % (str(e),))
            return

    def get_tweet(self, msg_id):
        """
        Pull tweet information.

        @param msg_id   - id of the tweet.
        @returns        - formatted string representing the tweet.
        """
        try:
            html  = requests.get(
                    'https://api.twitter.com/1.1/statuses/show/%s.json' % (msg_id,),
                    auth=self._twitter_auth)
            html.raise_for_status()
        except requests.exceptions.RequestException, e:
            log.err("Couldn't get tweet %s: %s" % (msg_id, str(e)))
            return

        msg =  "%s (%s) tweeted: %s" % (
            html.json()['user']['name'],
            html.json()['user']['screen_name'],
            html.json()['text'])

        return msg

    def get_title(self, url):
        """
        Get the title of the specified url.  If there are any redirects, they
        will first be followed before pulling the title.  Image and pdf links
        will be ignored.

        @param url  - url to pull title for.
        @return     - title if found.
        """
        while True:
            try:
                html = requests.get(url, verify=False)
                html.raise_for_status()
            except requests.exceptions.RequestException, e:
                log.err(str(e))
                return

            if html.headers['content-type'].startswith('image'):
                return
            elif html.headers['content-type'].startswith('application/pdf'):
                return
            else:
                parsed = soup(html.text, 'html.parser')
                if parsed.title is None:
                    redirect = self._meta_redirect(parsed)
                    if not redirect:
                        log.err("Couldn't parse content from %s" % (url,))
                        return
                    else:
                        url = redirect
                else:
                    break

        msg = 'Link: %s' % (parsed.title.text,)
        msg = msg.strip().replace('\n', ' ')

        return msg

    @staticmethod
    def _meta_redirect(content):
        redirect = content.find('meta', attrs={'http-equiv': 'Refresh'})
        if not redirect:
            redirect = content.find('meta', attrs={'http-equiv': 'refresh'})

        if redirect:
            url = redirect['content'].split('url=')[1]
            return url

    @irc_passive('get more information about links')
    def linker(self, user, channel, msg):
        urls = self._url_re.findall(msg)
        for url in urls:
            if self._twitter_auth is not None:
                twitter_url = self._twitter_re.match(url)
                if twitter_url:
                    msg = self.get_tweet(twitter_url.group(1))
                    self._proto.send_msg(channel, msg)
                    continue

            msg = self.get_title(url)
            if msg is not None:
                self._proto.send_msg(channel, msg)


