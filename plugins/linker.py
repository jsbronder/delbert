import re
import types

import requests
import requests_oauthlib
from twisted.python import log
from bs4 import BeautifulSoup as soup

twitter_auth = None

def tweet(proto, channel, msg_id):
    global twitter_auth
    if twitter_auth is None:
        auth_url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
        try:
            auth = requests_oauthlib.OAuth1(
                    config['app_key'],
                    config['app_secret'],
                    config['user_token'],
                    config['user_secret'])
        except Exception, e:
            log.err("Couldn't authenticate with twitter: %s " % (str(e),))
            return
        twitter_auth = auth
        
    try:
        html  = requests.get('https://api.twitter.com/1.1/statuses/show/%s.json' % (msg_id,), auth=twitter_auth)
        html.raise_for_status()
    except requests.exceptions.RequestException, e:
        log.err("Couldn't get tweet %s: %s" % (msg_id, str(e)))
        return

    msg =  "%s (%s) tweeted: %s" % (
        html.json()['user']['name'],
        html.json()['user']['screen_name'],
        html.json()['text'])

    if isinstance(msg, types.UnicodeType):
        msg = msg.encode('utf-8')

    proto.say(channel, msg)

def meta_redirect(content):
    redirect = content.find('meta', attrs={'http-equiv': 'Refresh'})
    if not redirect:
        redirect = content.find('meta', attrs={'http-equiv': 'refresh'})

    if redirect:
        url = redirect['content'].split('url=')[1]
        return url

def passive_linker(proto, channel, _, msg):
    exp = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(exp, msg)
    for url in urls:
        # Handle twitter links separately
        twitter_url = re.match('http[s]?://(?:www.)?twitter.com/.+/status/([0-9]+)', url)
        if twitter_url:
            tweet(proto, channel, twitter_url.group(1))
            continue

        while True:
            try:
                html = requests.get(url, verify=False)
                html.raise_for_status()
            except requests.exceptions.RequestException, e:
                log.err(str(e))
                return str(e)

            if html.headers['content-type'].startswith('image'):
                return
            elif html.headers['content-type'].startswith('application/pdf'):
                return
            else:
                parsed = soup(html.text)
                if parsed.title is None:
                    redirect = meta_redirect(parsed)
                    if not redirect:
                        log.err("Couldn't not parse content from %s" % (url,))
                        return
                    else:
                        url = redirect
                else:
                    break

        msg = 'Link: %s' % (parsed.title.text,)
        msg = msg.strip().replace('\n', ' ')

        if isinstance(msg, types.UnicodeType):
            msg = msg.encode('utf-8')

        proto.say(channel, msg)


