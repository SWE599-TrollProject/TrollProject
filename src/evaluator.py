from datetime import datetime, timedelta, time
from src import get_config
from .api import (Twit, PerspectiveAPI)


class Evaluator(object):
    def __init__(self, root_path):
        self.api = Twit(root_path).get_api()
        self.perspective = PerspectiveAPI(root_path)
        config = get_config(root_path)
        self.inactive_rate = config.getfloat('RATES', 'inactive_rate')
        self.bot_rate = config.getfloat('RATES', 'bot_rate')
        self.user = None
        self.tline = None

    def evaluate(self, screen_name):
        try:
            # check is user exists (or public)
            self.user = self.api.GetUser(screen_name=screen_name)
        except Exception as ex:
            return 404, {'error': {'message': ex.message}}

        try:
            self.tline = self.api.GetUserTimeline(screen_name=screen_name)
        except Exception as ex:
            return 404, {'error': {'message': ex.message}}

        def get_tweet_props(prop):
            return [t.AsDict()[prop] for t in self.tline]

        toxic_level = self.toxic_level(get_tweet_props('text'))
        bot_level = self.bot_level()
        inactivity_level = self.inactivity_level()

        return 200, {
            'result': {
                'bot_level': bot_level,
                'inactive_level': inactivity_level,
                'toxic_level': toxic_level,
                'account_basic': self.user.AsDict()
            }
        }

    def toxic_level(self, msgs):
        def get_toxicity(msg):
            tx = self.perspective.get_toxicity(msg)
            return tx['attributeScores']['TOXICITY']['summaryScore']['value']

        return sum(get_toxicity(msg) for msg in msgs) / len(msgs)

    def bot_level(self):
        # check how many same messages and hashtags used by account
        return 1

    def inactivity_level(self):
        # check the frequency of messages
        last_msg = self.tline[0].AsDict()
        first_msg = self.tline[-1].AsDict()

        get_date = lambda x: datetime.strptime(x['created_at'],
                                           '%a %b %d %H:%M:%S +0000 %Y')

        last_tweet_date = get_date(last_msg)
        first_tweet_date = get_date(first_msg)
        last_first_diff = abs((last_tweet_date - first_tweet_date).days)
        active_time_avg = len(self.tline) / last_first_diff

        if active_time_avg > self.inactive_rate:
            return {'inactive': False, 'tweets_per_day': active_time_avg}
        else:

            return active_time_avg
