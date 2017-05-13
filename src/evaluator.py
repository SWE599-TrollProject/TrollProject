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

    def evaluate(self, screen_name):
        try:
            # check is user exists (or public)
            self.user = self.api.GetUser(screen_name=screen_name)
        except Exception as ex:
            return 404, {'error': {'message': ex.message}}

        try:
            self.tline = [t.AsDict() for t in self.api.GetUserTimeline(
                screen_name=screen_name, count=100)]

            if len(self.tline) == 0:
                return 200, {
                    'result': 'inactive'
                }
        except Exception as ex:
            return 404, {'error': {'message': ex.message}}

        def get_tweet_props(prop):
            return [t[prop] for t in self.tline]

        try:
            msg_for_toxicity = " ".join(get_tweet_props('text'))
            toxic_level = self.toxic_level(msg_for_toxicity[:2800])
            bot_level = self.bot_level()
            inactivity_level = self.inactivity_level()
        except Exception as ex:
            return 500, {'error': {'message': ex.message}}

        return 200, {
            'result': {
                'bot_level': bot_level,
                'inactive_level': inactivity_level,
                'troll_level': toxic_level,
                # 'account_basic': self.user.AsDict()
            }
        }

    @staticmethod
    def get_date(x):
        return datetime.strptime(x['created_at'], '%a %b %d %H:%M:%S +0000 %Y')

    def toxic_level(self, msg):
        tx = self.perspective.get_toxicity(msg)
        return {k: v['summaryScore']['value'] for k,v in tx['attributeScores'].items()}

    def bot_level(self):
        # calculate retweet speed
        rt_deltas = []
        t_deltas = []
        last_tweet_time = None
        for tweet in self.tline:
            t_time = self.get_date(tweet)
            if 'retweeted_status' in tweet:
                rt_time = self.get_date(tweet['retweeted_status'])
                rt_deltas.append(abs((rt_time - t_time).seconds))
            if last_tweet_time:
                t_deltas.append(abs((last_tweet_time - t_time).seconds))
                last_tweet_time = t_time
            else:
                last_tweet_time = t_time

        shortest_rt, grouped_rtd = 0, []
        shortest_t, grouped_td = 0, []
        if len(rt_deltas) > 0:
            sorted_rtd = sorted(rt_deltas)
            shortest_rt = sorted_rtd[0]
            grouped_rtd = list(set(sorted_rtd))

        if len(t_deltas) > 0:
            sorted_td = sorted(t_deltas)
            shortest_t = sorted_td[-1]
            grouped_td = list(set(sorted_td))

        is_bot_suspect = False
        if len(grouped_td) > 0:
            if 0.9 >= len(grouped_td) / len(sorted_td) >= 0.1:
                is_bot_suspect = True
        if len(grouped_rtd) > 0:
            if 0.9 >= len(grouped_rtd) / len(sorted_rtd) >= 0.1:
                is_bot_suspect = True

        return {
            'is_bot_suspect': is_bot_suspect,
            'shortest_rt': shortest_rt,
            'shortest_t': shortest_t
        }

    def inactivity_level(self):
        # check the frequency of messages
        last_msg = self.tline[0]
        first_msg = self.tline[-1]

        last_tweet_date = self.get_date(last_msg)
        first_tweet_date = self.get_date(first_msg)
        last_first_diff = abs((last_tweet_date - first_tweet_date).days)
        today_last_diff = abs((datetime.today() - last_tweet_date).days)
        if last_first_diff == 0:
            last_first_diff = 1
        active_time_avg = len(self.tline) / last_first_diff

        if active_time_avg > self.inactive_rate and today_last_diff < self.inactivity_tolerance:
            return {'inactive': False, 'tweets_per_day': active_time_avg}
        else:
            data = {'inactive': True, 'tweets_per_day': active_time_avg}
            if today_last_diff > self.inactivity_tolerance:
                data.update({'inactive_for_days': today_last_diff})
            return data
