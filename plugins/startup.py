import types

import requests
from twisted.python import log

def cmd_startup(proto, _, channel, __):
    try:
        html = requests.get('http://itsthisforthat.com/api.php?text', verify=False)
    except requests.exceptions.RequestException, e:
        log.err(str(e))
        return str(e)

    msg = html.content.lower().capitalize()
    if isinstance(msg, types.UnicodeType):
        msg = msg.encode('utf-8')

    proto.say(channel, msg)

