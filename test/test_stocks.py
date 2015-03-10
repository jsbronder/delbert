import unittest

import httpretty

import base

class StocksTester(unittest.TestCase):
    def setUp(self):
        self._stocks, self._exc = base.load_plugin_and_excs('stocks.py', 'Stocks')
        self._proto = base.TestProto([self._stocks])

    @base.net_test
    def test_quote(self):
        m = self._stocks.get_quote('AAPL')
        self.assertIn('Status', m)
        self.assertEqual(m['Status'], 'SUCCESS')

        for k in ('High', 'Name', 'LastPrice', 'Timestamp', 'Symbol', 'ChangePercent',
                'Volume', 'ChangePercentYTD', 'MSDate', 'ChangeYTD', 'MarketCap',
                'Open', 'Change', 'Low'):
            self.assertIn(k, m)

        with self.assertRaises(self._exc['InvalidSymbolError']):
            m = self._stocks.get_quote('BLAH')

    def test_msg(self):
        body = '''{"Status":"SUCCESS",
                    "Name":"Apple Inc",
                    "Symbol":"AAPL",
                    "LastPrice":124.31,
                    "Change":-2.83,
                    "ChangePercent":-2.22589271669026,
                    "Timestamp":"Tue Mar 10 13:00:42 UTC-04:00 2015",
                    "MSDate":42073.5421527937,
                    "MarketCap":724074423880,
                    "Volume":5845689,
                    "ChangeYTD":110.38,
                    "ChangePercentYTD":12.6200398622939,
                    "High":127.21,
                    "Low":123.8,
                    "Open":126.62}'''
        httpretty.enable()
        httpretty.register_uri(
                httpretty.GET,
                'http://dev.markitondemand.com/Api/v2/Quote/json?symbol=AAPL',
                body=body,
                content_type='application/json')


        self._proto.privmsg('tester', base.TEST_CHANNEL, '!quote AAPL')
        self.assertEqual(1, len(self._proto.msgs))
        self.assertEqual(self._proto.msgs[0][2], u'Apple Inc [AAPL], 124.31, -2.83(-2.23%)')
        httpretty.disable()

def main():
    unittest.main()

if __name__ == '__main__':
    main()
