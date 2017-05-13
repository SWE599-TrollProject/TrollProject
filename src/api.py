import twitter
import json
import requests
from src import get_config


class Twit(object):
    def __init__(self, root_path):
        config = get_config(root_path)
        self.consumer_key = config.get('TWITTER', 'consumer_key')
        self.consumer_secret = config.get('TWITTER', 'consumer_secret')
        self.access_key = config.get('TWITTER', 'access_key')
        self.access_secret = config.get('TWITTER', 'access_secret')

    def get_api(self):
        return twitter.Api(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token_key=self.access_key,
            access_token_secret=self.access_secret)


class PerspectiveAPI(object):
    def __init__(self, root_path):
        config = get_config(root_path)
        self.perspective_key = config.get('PERSPECTIVEAPI', 'key')

    def get_toxicity(self, text):
        url = 'https://commentanalyzer.googleapis.com/' \
              'v1alpha1/comments:analyze?key={}'.format(self.perspective_key)
        data = {
            'comment': {'text': text},
            'languages': ['en'],
            'requestedAttributes': {
                'TOXICITY': {},
                # 'ATTACK_ON_AUTHOR': {},
                # 'ATTACK_ON_COMMENTER': {},
                # 'INCOHERENT': {},
                # 'INFLAMMATORY': {},
                'OBSCENE': {},
                # 'OFF_TOPIC': {},
                'SPAM': {},
                # 'UNSUBSTANTIAL': {},
                # 'LIKELY_TO_REJECT': {}
            }
        }

        resp = requests.post(url=url, data=json.dumps(data))

        return resp.json()
