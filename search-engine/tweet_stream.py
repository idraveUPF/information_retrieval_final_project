import simplejson as json
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from utils import get_terms
import argparse
import nltk

class MyListener(StreamListener):
    
    def __init__(self, max_tweets, output_file='Output.json'):
        super(StreamListener, self).__init__()
        self.num_tweets = 0
        self.max_tweets = max_tweets
        self.output_file = output_file

    def on_data(self, data):
        try:
            with open(self.output_file, 'a') as f:
                jdata = json.loads(data)
                filter_data = {}
                if 'extended_tweet' in jdata: 
                    filter_data['Tweet_text'] = jdata['extended_tweet']['full_text']
                    hashtags = jdata['extended_tweet']['entities']['hashtags']
                else:
                    filter_data['Tweet_text'] = jdata['text']
                    hashtags = jdata['entities']['hashtags']
                filter_data['Hashtags'] = [ht['text'] for ht in hashtags]
                filter_data['Username'] = jdata['user']['screen_name']
                filter_data['ID'] = jdata['id']
                filter_data['Date'] = jdata['created_at']
                filter_data['Likes'] = jdata['favorite_count']
                filter_data['URL'] = f"https://twitter.com/{jdata['user']['screen_name']}/status/{jdata['id']}"
                filter_data['Number_Retweets'] = jdata['retweet_count']
                if 'retweeted_status' in jdata: 
                    filter_data['is_Retweeted'] = True 
                    filter_data['Tweet_Retweeted'] = jdata['retweeted_status']['id']
                else: 
                    filter_data['is_Retweeted'] = False

                filter_data['terms'] = get_terms(filter_data['Tweet_text'])
                print(filter_data)
                
                self.num_tweets += 1
                f.write(json.dumps(filter_data)+'\n')

                # Setting a limit in the number of tweets collected
                if self.num_tweets < self.max_tweets:
                    return True
                else:
                    return False

        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True
 
    def on_error(self, status):
        print('Error :', status.place)
        return False

KEYWORDS = ["BlackLivesMatter", "AllLivesMatter", "BlueLivesMatter", "BLM", "blackpower", "blackpride", "africanamerican", "racism", "blackhistory", "equality", "policebrutality"]

def parse_args():
    pass


if __name__ == '__main__':
    nltk.download('stopwords')

    consumer_key = 'UPtQiALNjB7rWxcIY8CB9IXmb'
    consumer_secret = 'lsU5NELQCDfE7eGs0f2fraobK34LoF7X0OSreaOAdLR7n7uwv8'
    access_token = '3796381515-0VrTXAZlasSMTWGlYBDa5djTsKjS6hl1eqrHmIt'
    access_secret = 'juiVqZVBAoqQyFjXfsWWt8LkBM0ikqpNsWmhHrh8ZyHA3'

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    twitter_stream = Stream(auth, MyListener(5))
    twitter_stream.filter(track=KEYWORDS, languages=['en']) # Add your keywords and other filters

    print('_______ End _______')