import json

import requests
from twisted.python import log

from twisted.web import (server, resource)
from twisted.internet import reactor


class GithubHook(resource.Resource):
    """
    Web handler for github webhooks
    """
    isLeaf = True

    def __init__(self):
        resource.Resource.__init__(self)
        self._push_handlers = set()
        self._issue_handlers = set()

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

    def register_issue_handler(self, callback):
        """
        Register a handler for issue events

        @param callback - callback for issue events.  The function should
                          accept a dictionary which describes the event
        """
        self._issue_handlers.add(callback)

    def unregister_issue_handler(self, callback):
        """
        Unregister a issue event handler

        @param callback - callback to unregister
        """
        self._issue_handlers.remove(callback)

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
                for cb in self._push_handlers:
                    cb(data)
            elif event == 'issues':
                for cb in self._issue_handlers:
                    cb(data)
        except Exception:
            log.err()

        return ''


class Github(Plugin):  # noqa: F821
    def __init__(self, config=None):
        super(Github, self).__init__('github')
        self._config = config if config is not None else {}
        self._hook = None
        self._repos = self._config.get('repos', {})

        if 'listen_port' in self._config:
            self._handler = GithubHook()
            self._handler.register_push_handler(self.handle_push)
            self._handler.register_issue_handler(self.handle_issue)
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
                html.json()['created_on'],
                html.json()['status'])
        else:
            return '%s:  [%s] %s' % (
                html.json()['created_on'],
                html.json()['status'],
                html.json()['body'])

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

    @irc_command('return current github status')  # noqa: F821
    def github(self, user, channel, args):
        if channel == self.nickname:
            nick = get_nick(user)  # noqa: F821
            self._proto.send_notice(nick, self.status)
        else:
            self._proto.send_notice(channel, self.status)

    def handle_push(self, data):
        """
        Handle github push events

        @param data - dictionary describing the push event.
        """
        repo = '%s/%s' % (
            data['repository']['owner']['name'],
            data['repository']['name'])
        log.msg('Got push event for %s' % (repo,))

        if repo not in self._repos:
            return

        channels = [
            channel
            for channel, events in self._repos[repo].items()
            if 'push' in events
        ]

        log.msg('%s' % (channels,))
        if len(channels) == 0:
            return

        msgs = self._push_msgs(repo, data)

        for channel in channels:
            for msg in msgs:
                self._proto.send_notice(channel, msg)

    def handle_issue(self, data):
        """
        Handle github issue events

        @param data - dictionary describing the opened event.
        """
        action = data.get('action')
        if action is None or action != 'opened':
            return

        repo = data['repository']['full_name']
        log.msg('Got issue opened event for %s' % (repo,))

        if repo not in self._repos:
            return

        channels = [
            channel
            for channel, events in self._repos[repo].items()
            if 'issues' in events
        ]

        log.msg('%s' % (channels,))
        if len(channels) == 0:
            return

        msg = '[%s] %s opened issue %d: %s -- %s' % (
                repo,
                data['issue']['user']['login'],
                data['issue']['number'],
                data['issue']['title'],
                self.shorten(data['issue']['url']))

        for channel in channels:
            self._proto.send_notice(channel, msg)

    def _push_msgs(self, repo, data):
        """
        Create messages from a push event for the given repo

        @param repo - repository getting pushed to
        @param data - dictionary describing push event
        @return     - list of messages describing the push event
        """
        msgs = []
        n_commits = len(data['commits'])

        if n_commits == 0:
            msgs.append('[%s] %s deleted branch %s' % (
                    repo,
                    data['pusher']['name'],
                    data['ref'].replace('refs/heads/', '')))
            return msgs

        msgs.append('[%s] %s pushed %d commit%s to %s:' % (
            repo,
            data['pusher']['name'],
            n_commits,
            '' if n_commits <= 1 else 's',
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
