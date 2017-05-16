from datetime import datetime
from src import get_config
from src.api import (Twit, PerspectiveAPI)


class Evaluator(object):
    def __init__(self, root_path):
        self.api = Twit(root_path).get_api()
        self.perspective = PerspectiveAPI(root_path)
        config = get_config(root_path)
        self.inactive_rate = config.getfloat('LIMITS', 'inactive_rate')
        self.inactivity_tolerance = config.getint('LIMITS', 'inactivity_tolerance')
        self.bot_rate = config.getfloat('LIMITS', 'bot_rate')
        self.user = None
        self.tline = None

    def evaluate(self, screen_name):
        try:
            # check is user exists (or public)
            self.user = self.api.GetUser(screen_name=screen_name)
        except Exception as ex:
            return 404, ex.message

        try:
            self.tline = [t.AsDict() for t in self.api.GetUserTimeline(
                screen_name=screen_name, count=100)]

            if len(self.tline) == 0:
                return 200, {
                    'result': 'inactive'
                }
        except Exception as ex:
            return 404, ex.message

        def get_tweet_props(prop):
            return [t[prop] for t in self.tline]

        try:
            msg_for_toxicity = " ".join(get_tweet_props('text'))
            msg = msg_for_toxicity.encode(encoding='utf-8')[:3000]
            toxic_level = self.toxic_level(msg.decode(errors='ignore'))
            bot_level = self.bot_level()
            activity_level = self.activity_level()
        except Exception as ex:
            return 500, ex.message

        return 200, {
            'result': {
                'bot_level': bot_level,
                'activity_level': activity_level,
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

            l1 = [0.5, 0.5, 0.5, 0.6, 0.6, 0.7, 0.7, 0.7, 0.7]
            l2 = [0.5, 0.6, 0.7]

            gr = [0.5, 0.6, 0.7]

        if len(t_deltas) > 0:
            sorted_td = sorted(t_deltas)
            shortest_t = sorted_td[0]
            grouped_td = list(set(sorted_td))

        is_bot_suspect = False
        a, b = None, None
        if len(grouped_td) > 0:
            bot_rate = len(grouped_td) / len(sorted_td)
            if self.max_bot_rate >= bot_rate >= self.min_bot_rate:
                a = len(grouped_td) / len(sorted_td)
                is_bot_suspect = True
        if len(grouped_rtd) > 0:
            bot_rate = len(grouped_rtd) / len(sorted_rtd)
            if self.max_bot_rate >= bot_rate >= self.min_bot_rate:
                b = len(grouped_rtd) / len(sorted_rtd)
                is_bot_suspect = True
        if a or b:
            if a and b:
                suspect_rate = (a + b) / 2
            else:
                suspect_rate = a or b
        else:
            suspect_rate = 0

        return {
            'is_bot_suspect': is_bot_suspect,
            'shortest_rt': shortest_rt,
            'shortest_t': shortest_t,
            'suspect_rate': suspect_rate
        }

    def activity_level(self):
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
