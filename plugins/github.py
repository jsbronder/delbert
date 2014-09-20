import json

import requests
from twisted.python import log

from twisted.web import (server, resource, http)
from twisted.internet import reactor

class GithubHook(resource.Resource):
    """
    Web handler for github webhooks
    """
    isLeaf = True

    def __init__(self):
        resource.Resource.__init__(self)
        self._push_handlers = set()

    def register_push_handler(self, callback):
        """
        Register a handler for push events

        @param callback - callback for push events.  The function should
                          accept a dictionary which describes the event
        """
        self._push_handlers.add(callback)

    def unregister_push_handler(self, callback):
        """
        Unregister a push event handler

        @param callback - callback to unregister
        """
        self._push_handlers.remove(callback)

    def render_POST(self, req):
        event = req.getHeader('X-Github-Event')
        if event is None:
            return 'No X-Github-Event in header'

        try:
            data = json.loads(req.content.read())
        except ValueError:
            msg = 'Failed to parse data from %s' % (req.getClientIP(),)
            log.err(msg)
            return msg

        try:
            if event == 'push':
                _ = [cb(data) for cb in self._push_handlers]
        except Exception:
            log.err()

        return ''


class Github(Plugin):
    def __init__(self, config={}):
        super(Github, self).__init__('github')
        self._config = config
        self._hook = None
        self._repos = self._config.get('repos', {})

        if 'listen_port' in self._config:
            self._handler = GithubHook()
            self._handler.register_push_handler(self.handle_push)
            site = server.Site(self._handler)
            reactor.listenTCP(self._config['listen_port'], site)

    @property
    def status(self):
        """
        Return current github status.
        """
        try:
            html = requests.get(
                    'https://status.github.com/api/last-message.json',
                    verify=False)
        except requests.exceptions.RequestException, e:
            log.err(str(e))
            return

        if html.json()['status'] == 'good':
            return '%s:  [%s]' % (
                html.json()['created_on'], html.json()['status'])
        else:
            return '%s:  [%s] %s' % (
                html.json()['created_on'], html.json()['status'], html.json()['body'])

    @staticmethod
    def shorten(url):
        """
        Shorten a github url

        @param url  - full github url to shorten
        @return     - shortened url
        """
        try:
            req = requests.post('http://git.io/', data={'url': url})
            req.raise_for_status()
        except Exception, e:
            log.err('Failed to git.io shorten %s: %s' % (url, str(e)))
            return url

        if req.status_code == 201 and 'location' in req.headers:
            return req.headers['location']
        else:
            return url

    @irc_command('return current github status')
    def github(self, user, channel, args):
        if channel == self.nickname:
            nick = get_nick(user)
            self._proto.send_notice(nick, self.status)
        else:
            self._proto.send_notice(channel, self.status)

    def handle_push(self, data):
        """
        Handle github push events

        @param data - dictionary describing the push event.
        """
        repo = '%s/%s' % (data['repository']['owner']['name'], data['repository']['name'])
        log.msg('Got push event for %s' % (repo,))

        if not repo in self._repos:
            return

        channels = [channel
                for channel, events in self._repos[repo].items()
                if 'push' in events]

        log.msg('%s' % (channels,))
        if len(channels) == 0:
            return

        msgs = self._push_msgs(repo, data)

        for channel in channels:
            _ = [self._proto.send_notice(channel, msg) for msg in msgs]

    def _push_msgs(self, repo, data):
        """
        Create messages from a push event for the given repo

        @param repo - repository getting pushed to
        @param data - dictionary describing push event
        @return     - list of messages describing the push event
        """
        msgs = []
        n_commits = len(data['commits'])

        msgs.append('[%s] %s pushed %d commit%s to %s:' % (
            repo,
            data['pusher']['name'],
            n_commits,
            '' if n_commits <=1 else 's',
            data['ref'].replace('refs/heads/', '')))

        for commit in data['commits']:
            header = commit['message'].split('\n', 1)[0]
            if len(header) > 40:
                swap_index = header.rindex(' ')
                header = header[:swap_index] + ' ...'

            msgs.append('    <%s> %s (%s)  %s' % (
                commit['id'][:7],
                header,
                commit['author'].get('username', commit['author']['email']),
                self.shorten(commit['url']),))

        return msgs

