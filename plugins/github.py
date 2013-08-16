import types

import requests
from twisted.python import log
from string import Template

response = Template('${created_on}: ${body}')

def cmd_github(proto, _, channel, __):
    try:
        html = requests.get('https://status.github.com/api/messages.json', verify=False)
    except requests.exceptions.RequestException, e:
        log.err(str(e))
        return str(e)

    msgs = html.json()

    if len(msgs) > 0:
      proto.say(channel, response.substitute(msgs[0]))

