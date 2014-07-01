import requests

class WorldCup(Plugin):
    def __init__(self, config={}):
        super(WorldCup, self).__init__('wc')

    @irc_command('Get current score from world cup')
    def wc(self, user, channel, args):
        send_to = get_nick(user) if channel == self.nickname else channel
        try:
            response = requests.get('http://worldcup.sfg.io/matches/current')
            results = response.json()
            for result in results:
                away_team = result['away_team']['country']
                home_team = result['home_team']['country']
                away_goals = result['away_team']['goals']
                home_goals = result['home_team']['goals']
                msg = '%s %d-%d %s' % (
                        home_team,
                        home_goals,
                        away_goals,
                        away_team)
                self._proto.send_notice(send_to, msg)

        except Exception as e:
            self._proto.send_notice(send_to, 'unable to retrieve result')
