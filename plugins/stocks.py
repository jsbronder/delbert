import requests

from twisted.python import log


class InvalidSymbolError(Exception):
    pass


class Stocks(Plugin):  # noqa: F821
    def __init__(self, config=None):
        super(Stocks, self).__init__('stocks')
        self._base_url = 'http://dev.markitondemand.com/Api/v2/'
        self._config = config if config is not None else {}

    def get_quote(self, symbol):
        """
        Get a stock quote for the specified symbol.  Return is a dictionary
        containing the information documented at
        http://dev.markitondemand.com/#doc_quote

        @param symbol   - symbol for which to lookup quote
        @return         - stock quote
        """
        try:
            url = self._base_url + 'Quote/json?symbol=%s' % (symbol,)
            html = requests.get(url, verify=False)
        except requests.exceptions.RequestException, e:
            log.err(str(e))
            return

        ret = html.json()

        if ret.get('Message', '').startswith('No symbol matches found for '):
            raise InvalidSymbolError()

        return html.json()

    @irc_command(  # noqa: F821
        'Lookup the current quote for the specified ticker symbol')
    def quote(self, user, channel, args):
        log.msg('Pulling quotes for symbols: %s' % (','.join(args.split())))

        for arg in args.split():
            try:
                quote = self.get_quote(arg)
            except InvalidSymbolError:
                msg = 'Invalid Symbol %s' % (arg,)
            else:
                msg = '%s [%s], %.2f, %.2f(%.2f%%)' % (
                        quote['Name'],
                        quote['Symbol'],
                        quote['LastPrice'],
                        quote['Change'],
                        quote['ChangePercent'])

            if channel == self.nickname:
                n = get_nick(user)  # noqa: F821
                self._proto.send_msg(n, msg)
            else:
                self._proto.send_notice(channel, msg)
