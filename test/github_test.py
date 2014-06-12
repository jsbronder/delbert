import json
import re
import unittest

import base

commit_data = """
{
  "ref": "refs/heads/master",
  "after": "a96dbcb0e566ba8330b2b24ce0f31ed53a29e0ff",
  "before": "4a666d1d66e5db362742acee3c6fed4ca0b77a97",
  "created": false,
  "deleted": false,
  "forced": false,
  "compare": "https://github.com/jsbronder/test-hooks/compare/4a666d1d66e5...a96dbcb0e566",
  "commits": [
    {
      "id": "a96dbcb0e566ba8330b2b24ce0f31ed53a29e0ff",
      "distinct": true,
      "message": "a commit message",
      "timestamp": "2014-06-11T18:39:09-04:00",
      "url": "https://github.com/jsbronder/test-hooks/commit/a96dbcb0e566ba8330b2b24ce0f31ed53a29e0ff",
      "author": {
        "name": "Justin Bronder",
        "email": "jsbronder@gmail.com",
        "username": "jsbronder"
      },
      "committer": {
        "name": "Justin Bronder",
        "email": "jsbronder@gmail.com",
        "username": "jsbronder"
      },
      "added": [

      ],
      "removed": [

      ],
      "modified": [
        "1"
      ]
    }
  ],
  "head_commit": {
    "id": "a96dbcb0e566ba8330b2b24ce0f31ed53a29e0ff",
    "distinct": true,
    "message": "4",
    "timestamp": "2014-06-11T18:39:09-04:00",
    "url": "https://github.com/jsbronder/test-hooks/commit/a96dbcb0e566ba8330b2b24ce0f31ed53a29e0ff",
    "author": {
      "name": "Justin Bronder",
      "email": "jsbronder@gmail.com",
      "username": "jsbronder"
    },
    "committer": {
      "name": "Justin Bronder",
      "email": "jsbronder@gmail.com",
      "username": "jsbronder"
    },
    "added": [

    ],
    "removed": [

    ],
    "modified": [
      "1"
    ]
  },
  "repository": {
    "id": 20746319,
    "name": "test-hooks",
    "url": "https://github.com/jsbronder/test-hooks",
    "description": "testing webhooks",
    "watchers": 0,
    "stargazers": 0,
    "forks": 0,
    "fork": false,
    "size": 0,
    "owner": {
      "name": "jsbronder",
      "email": "jsbronder@gmail.com"
    },
    "private": false,
    "open_issues": 0,
    "has_issues": true,
    "has_downloads": true,
    "has_wiki": true,
    "created_at": 1402525177,
    "pushed_at": 1402526351,
    "master_branch": "master"
  },
  "pusher": {
    "name": "jsbronder",
    "email": "jsbronder@gmail.com"
  }
}
"""


class GithubTester(unittest.TestCase):
    """
    Test the github plugin without webhook configuration.
    """
    def setUp(self):
        config = {
            'repos': {
                'jsbronder/test-hooks': {
                    base.TEST_CHANNEL: ['push']
                },
            },
        }
        self._plugin = base.load_plugin('github.py', 'Github', config=config)
        self._plugin.shorten = lambda x : '<shorturl>'
        self._proto = base.TestProto([self._plugin])
        self._re = re.compile('^[0-9-]{10}T[0-9:]{8}Z:  \[[a-z]*\]')


    def test_query(self):
        m = self._plugin.status
        self.assertIsNotNone(self._re.search(m))

    def test_msg(self):
        self._proto.privmsg('tester', base.TEST_CHANNEL, '!github')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertIsNotNone(self._re.search(self._proto.msgs[0][2]))

    def test_webhook_push(self):
        data = json.loads(commit_data) 
        self._plugin.handle_push(data)
        self.assertEqual(2, len(self._proto.msgs))
        self.assertIn('pushed 1 commit to', self._proto.msgs[0][2])
        self.assertIn('<shorturl>', self._proto.msgs[1][2])
        self.assertIn('a commit message', self._proto.msgs[1][2])
        self.assertIn('a96dbcb', self._proto.msgs[1][2])


def main():
    unittest.main()

if __name__ == '__main__':
    main()
