import simplejson as json
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from utils import get_terms
from user import User
import argparse
from pathlib import Path
import nltk
import time

class MyListener(StreamListener):
    
    def __init__(self, max_tweets, output_file=None, user_file=None):
        super(StreamListener, self).__init__()
        self.num_tweets = 0
        self.max_tweets = max_tweets
        if output_file == None or user_file == None:
            if not OUTPUT_JSON.parent.is_dir():
                OUTPUT_JSON.parent.mkdir(parents=False)
        self.output_file = output_file if output_file is not None else str(OUTPUT_JSON)
        self.user_file = user_file if user_file is not None else str(OUTPUT_USER)
        self.users = {}
        self.tweet_ids = set()

    def on_data(self, data):
        try:
            with open(self.output_file, 'a') as f:
                jdata = json.loads(data)
                #pprint.PrettyPrinter().pprint(jdata)
                filter_data = self.get_tweet(jdata)
                if filter_data['ID'] in self.tweet_ids:
                    return
                self.tweet_ids.add(filter_data['ID'])
                self.num_tweets += 1
                print('%d / %d' % (self.num_tweets, self.max_tweets), end='\r')
                f.write(json.dumps(filter_data)+'\n')

                # Setting a limit in the number of tweets collected
                if self.num_tweets < self.max_tweets:
                    return True
                else:
                    with open(self.user_file, 'a') as uf:
                        user_data = {user.id: user.to_json() for user in self.users.values()}
                        uf.write(json.dumps(user_data))
                    return False

        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    def get_tweet(self, jdata):
        filter_data = {}
        if jdata['user']['id'] not in self.users:
            uid = jdata['user']['id']
            uname = jdata['user']['screen_name']
            urt = {}
            self.users[uid] = User(uid, uname, urt)
        if 'retweeted_status' in jdata:
            filter_data = self.get_tweet(jdata['retweeted_status'])
            self.users[jdata['user']['id']].add_mention(filter_data['UserId'])
        else:
            if 'extended_tweet' in jdata:
                filter_data['Tweet_text'] = jdata['extended_tweet']['full_text']
                hashtags = jdata['extended_tweet']['entities']['hashtags']
            else:
                filter_data['Tweet_text'] = jdata['text']
                hashtags = jdata['entities']['hashtags']
            filter_data['Hashtags'] = [ht['text'] for ht in hashtags]
            filter_data['UserId'] = jdata['user']['id']
            filter_data['ID'] = jdata['id']
            filter_data['Date'] = jdata['created_at']
            filter_data['Likes'] = jdata['favorite_count']
            filter_data['URL'] = f"https://twitter.com/{jdata['user']['screen_name']}/status/{jdata['id']}"
            filter_data['Number_Retweets'] = jdata['retweet_count']

            filter_data['terms'] = get_terms(filter_data['Tweet_text'])
        return filter_data

    def on_error(self, status):
        print('Error :', status.place)
        return False

KEYWORDS = ["BlackLivesMatter", "AllLivesMatter", "BlueLivesMatter", "BLM", "blackpower", "blackpride", "africanamerican", "racism", "blackhistory", "equality", "policebrutality"]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-N', type=int, default=1000, help='Number of tweets')
    parser.add_argument('-output', default=None, help='Output json of tweets')
    return parser.parse_args()

#OUTPUT_JSON = Path(__file__).parent.parent.parent/'res'/'Output.json'
#OUTPUT_USER = Path(__file__).parent.parent.parent/'res'/'Users.json'
OUTPUT_JSON = Path('/home/ivan/Documents/upf/inforetrieval/finalproject/information_retrieval_final_project/res/Output.json')
OUTPUT_USER = Path('/home/ivan/Documents/upf/inforetrieval/finalproject/information_retrieval_final_project/res/Users.json')

if __name__ == '__main__':
    nltk.download('stopwords')

    consumer_key = 'UPtQiALNjB7rWxcIY8CB9IXmb'
    consumer_secret = 'lsU5NELQCDfE7eGs0f2fraobK34LoF7X0OSreaOAdLR7n7uwv8'
    access_token = '3796381515-0VrTXAZlasSMTWGlYBDa5djTsKjS6hl1eqrHmIt'
    access_secret = 'juiVqZVBAoqQyFjXfsWWt8LkBM0ikqpNsWmhHrh8ZyHA3'

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    args = parse_args()
    start_time = time.time()
    twitter_stream = Stream(auth, MyListener(args.N, output_file=args.output))
    twitter_stream.filter(track=KEYWORDS, languages=['en']) # Add your keywords and other filters
    total_time = time.time() - start_time
    print('_______ End _______')
    print('Tweets: ', args.N)
    print('Total time: ', total_time)