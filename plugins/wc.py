import random

import requests

import delbert.plugin


class WorldCup(delbert.plugin.Plugin):
    def __init__(self, config={}):
        super(WorldCup, self).__init__('wc')

    @delbert.plugin.irc_command('Get current score from world cup')
    def wc(self, user, channel, args):
        if random.random() < 0.05:
            notice = "Fuckin' calm down {}, it's soccer.".format(user)
            self._proto.send_notice(channel, notice)
        else:
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
                    self._proto.send_notice(channel, msg)
            except Exception:
                self._proto.send_notice(channel, 'unable to retrieve result')
