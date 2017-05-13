from src import get_config
from .api import (Twit, PerspectiveAPI)


class Evaluator(object):
    def __init__(self, root_path):
        self.api = Twit(root_path).get_api()
        self.perspective = PerspectiveAPI(root_path)
        config = get_config(root_path)
        self.inactive_rate = config.getfloat('RATES', 'inactive_rate')
        self.bot_rate = config.getfloat('RATES', 'bot_rate')

    def evaluate(self, screen_name):

        def get_tweet_props(prop):
            return [t.AsDict()[prop] for t in tline]

        try:
            # check is user exists (or public)
            self.api.GetUser(screen_name=screen_name)
        except Exception as ex:
            return 404, {'error': {'message': ex.message}}

        try:
            tline = self.api.GetUserTimeline(screen_name=screen_name)
        except Exception as ex:
            return 404, {'error': {'message': ex.message}}

        toxic_level = self.toxic_level(get_tweet_props('text'))

        return 200, {
            'result': {
                'bot_rate': '',
                'inactive_rate': '',
                'toxicty': toxic_level
            }
        }

    def toxic_level(self, msgs):
        def get_toxicity(msg):
            tx = self.perspective.get_toxicity(msg)
            return tx['attributeScores']['TOXICITY']['summaryScore']['value']

        return sum(get_toxicity(msg) for msg in msgs) / len(msgs)
