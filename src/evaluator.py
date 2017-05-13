from datetime import datetime
from src import get_config
from .api import (Twit, PerspectiveAPI)


class Evaluator(object):
    def __init__(self, root_path):
        self.api = Twit(root_path).get_api()
        self.perspective = PerspectiveAPI(root_path)
        config = get_config(root_path)
        self.inactive_rate = config.getfloat('RATES', 'inactive_rate')
        self.inactivity_tolerance = config.getint('RATES', 'inactivity_tolerance')
        self.bot_rate = config.getfloat('RATES', 'bot_rate')
        self.user = None
        self.tline = None
        self.tline_with_replies = None

    def evaluate(self, screen_name):
        try:
            # check is user exists (or public)
            self.user = self.api.GetUser(screen_name=screen_name)
        except Exception as ex:
            return 404, {'error': {'message': ex.message}}

        try:
            self.tline = self.api.GetUserTimeline(screen_name=screen_name, exclude_replies=True)
            self.tline_with_replies = self.api.GetUserTimeline(screen_name=screen_name)

            if len(self.tline) == 0:
                return 200, {
                    'result': 'inactive'
                }
        except Exception as ex:
            return 404, {'error': {'message': ex.message}}

        def get_tweet_props(prop):
            return [t.AsDict()[prop] for t in self.tline]

        try:
            toxic_level = self.toxic_level(get_tweet_props('text'))
            bot_level = self.bot_level()
            inactivity_level = self.inactivity_level()
        except Exception as ex:
            return 500, {'error': {'message': ex.message}}

        return 200, {
            'result': {
                'bot_level': bot_level,
                'inactive_level': inactivity_level,
                'toxic_level': toxic_level,
                'account_basic': self.user.AsDict()
            }
        }

    @staticmethod
    def get_date(x):
        return datetime.strptime(x['created_at'], '%a %b %d %H:%M:%S +0000 %Y')

    def toxic_level(self, msgs):
        def get_toxicity(msg):
            tx = self.perspective.get_toxicity(msg)
            return tx['attributeScores']['TOXICITY']['summaryScore']['value']

        return sum(get_toxicity(msg) for msg in msgs) / len(msgs)

    def bot_level(self):
        # calculate retweet speed
        rt_deltas = []
        for t in self.tline:
            tweet = t.AsDict()
            if 'retweeted_status' in tweet:
                rt_time = self.get_date(tweet['retweeted_status'])
                t_time = self.get_date(tweet)
                rt_deltas.append(abs((rt_time - t_time).seconds))

        if len(rt_deltas) > 0:
            avg_rt_deltas = sum(rt_deltas) / len(rt_deltas)
            return avg_rt_deltas
        else:
            return 0

    def inactivity_level(self):
        # check the frequency of messages
        last_msg = self.tline[0].AsDict()
        first_msg = self.tline[-1].AsDict()

        last_tweet_date = self.get_date(last_msg)
        first_tweet_date = self.get_date(first_msg)
        last_first_diff = abs((last_tweet_date - first_tweet_date).days)
        today_last_diff = abs((datetime.today() - last_tweet_date).days)
        active_time_avg = len(self.tline) / last_first_diff

        if active_time_avg > self.inactive_rate and today_last_diff < self.inactivity_tolerance:
            return {'inactive': False, 'tweets_per_day': active_time_avg}
        else:
            data = {'inactive': True, 'tweets_per_day': active_time_avg}
            if today_last_diff > self.inactivity_tolerance:
                data.update({'inactive_for_days': today_last_diff})
            return data
