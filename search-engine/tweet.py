
class Tweet:
    def __init__(self, id, text, user, date, url,
                 hashtags, likes, retweets, is_retweet, retweeted=None):
        self.id = id
        self.text = text
        self.user = user
        self.date = date
        self.url = url
        self.hashtags = hashtags
        self.likes = likes
        self.retweets = retweets
        self.is_retweet = is_retweet
        self.tweet_retweeted = retweeted
        if self.is_retweet and self.tweet_retweeted == None:
            raise ValueError('No retweeted tweet')

def tokenize(text):
    pass

class TweetTokens(Tweet):
    def __init__(self, id, text, user, date, url,
                 hashtags, likes, retweets, is_retweet, retweeted=None):
        super().__init__(id, text, user, date, url,
                         hashtags, likes, retweets, is_retweet, retweeted)
        self.tokens = tokenize(text)
