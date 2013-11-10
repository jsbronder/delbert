import unittest

import base

class SupTester(unittest.TestCase):
    def setUp(self):
        self._plugin = base.load_plugin('sup.py', 'Sup')
        self._proto = base.TestProto([self._plugin])

    def test_greet(self):
        self._proto.userJoined('tester!~boihae@aihfeoif', base.TEST_CHANNEL)
        self.assertEqual(self._proto.msgs[0], ('msg', base.TEST_CHANNEL, 'tester: sup fucko'))

def main():
    unittest.main()

if __name__ == '__main__':
    main()
