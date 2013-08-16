import types

import requests
from twisted.python import log
from string import Template

response = Template('${created_on}: ${body}')

def cmd_github(proto, _, channel, __):
    try:
        html = requests.get('https://status.github.com/api/last-message.json', verify=False)
    except requests.exceptions.RequestException, e:
        log.err(str(e))
        return str(e)

    msg = '%s:  [%s] %s' % (html.json['created_on'], html.json['status'], html.json['body'])

    if isinstance(msg, types.UnicodeType):
        msg = msg.encode('utf-8')

    proto.notice(channel, msg)

