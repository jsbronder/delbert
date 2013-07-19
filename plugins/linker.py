import re
import types

import requests
from twisted.python import log
from bs4 import BeautifulSoup as soup

def tweet(proto, channel, msg_id):
    try:
        html = requests.get('https://api.twitter.com/1/statuses/show.json?id=%s' % (msg_id,))
        html.raise_for_status()
    except requests.exceptions.RequestException, e:
        log.err("Couldn't get tweet %s: %s" % (msg_id, str(e)))
        return

    msg =  "%s (%s) tweeted: %s" % (
        html.json['user']['name'],
        html.json['user']['screen_name'],
        html.json['text'])

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


