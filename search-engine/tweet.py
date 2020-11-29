
class Tweet:
    def __init__(self, id, text, user, date, url,
                 hashtags, likes, retweets, terms):
        self.id = id
        self.text = text
        self.user = user
        self.date = date
        self.url = url
        self.hashtags = hashtags
        self.likes = likes
        self.retweets = retweets
        self.terms = terms

    def __str__(self):
        pass
