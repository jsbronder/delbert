import re
import string
import types
import urllib

import requests
from bs4 import BeautifulSoup as soup

def passive_linker(proto, channel, msg):
    exp = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(exp, msg)
    for url in urls:
        try:
            html = requests.get(url)
        except requests.exceptions.RequestException, e:
            return str(e)
        
        if html.headers['content-type'].startswith('image'):
            title = u'Image'
        elif html.headers['content-type'].startswith('application/pdf'):
            title = u'PDF'
        else:
            parsed = soup(html.text)
            title = parsed.title.text
            title = title.lstrip(string.whitespace)

        try:
            isgd = requests.get('http://is.gd/create.php?format=json&url=%s' % (urllib.quote(url),))
            surl = isgd.json['shorturl']
        except requests.exceptions.RequestException, e:
            surl = u'is.gd failed :/'
            
        msg = '%s @ %s' % (title,  surl)
        if isinstance(msg, types.UnicodeType):
            msg = msg.encode('utf-8')

        proto.say(channel, msg)


