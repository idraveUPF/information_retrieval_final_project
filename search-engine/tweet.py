import json

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

    def get_terms(self):
        return self.terms

    @staticmethod
    def from_json(json_str):
        tweet_json = json.loads(json_str)
        return Tweet(
            tweet_json['ID'], tweet_json['Tweet_text'], tweet_json['UserId'],
            tweet_json['Date'], tweet_json['URL'], tweet_json['Hashtags'],
            tweet_json['Likes'], tweet_json['Number_Retweets'], tweet_json['terms']
        )

    def to_json(self):
        return {
            'ID': self.id,
            'Tweet_text': self.text,
            'UserId': self.user,
            'Date': self.date,
            'URL': self.url,
            'Hashtags': self.hashtags,
            'Likes': self.likes,
            'Number_Retweets': self.retweets,
            'terms': self.terms
        }

    def tf_idf_score(self, index):
        tweet_v = []
        tweet_tf = index.get_tf(self, self.id)
        idfs = index.get_idf(self)
        for i in range(len(query_tf)):
            tweet_v.append(tweet_tf[i] * idfs[i])
            query_v.append(query_tf[i] * idfs[i])

    def __str__(self):
        pass
