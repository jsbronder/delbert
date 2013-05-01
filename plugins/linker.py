import re
import types
import urllib

import requests
from twisted.python import log
from bs4 import BeautifulSoup as soup

def tweet(proto, channel, msg_id):
    try:
        html = requests.get('https://api.twitter.com/1/statuses/show.json?id=%s' % (msg_id,))
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

def passive_linker(proto, channel, user, msg):
    exp = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(exp, msg)
    for url in urls:
        # Handle twitter links separately
        twitter_url = re.match('http[s]?://(?:www.)?twitter.com/.+/status/([0-9]+)', url)
        if twitter_url:
            tweet(proto, channel, twitter_url.group(1))
            continue

        try:
            html = requests.get(url)
        except requests.exceptions.RequestException, e:
            log.err(str(e))
            return str(e)

        if html.headers['content-type'].startswith('image'):
            title = u'Image'
        elif html.headers['content-type'].startswith('application/pdf'):
            title = u'PDF'
        else:
            parsed = soup(html.text)
            title = parsed.title.text
            title = title.strip()
            title = title.replace('\n', ' ')

        surl = ''
        try:
            isgd = requests.get('http://is.gd/create.php?format=json&url=%s' % (urllib.quote(url),))

            if 'shorturl' in isgd.json:
                surl = isgd.json['shorturl']
            else:
                log.msg("Failed to get shorturl: %s" %
                    (isgd.json['errormessage'] if 'errormessage' in isgd.json else ''))
        except requests.exceptions.RequestException, e:
            log.err(str(e))

        msg = '%s%s%s' % (title, ' @ ' if surl else '',  surl)
        if isinstance(msg, types.UnicodeType):
            msg = msg.encode('utf-8')

        proto.say(channel, msg)


