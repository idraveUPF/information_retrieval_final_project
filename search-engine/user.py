import json
from index import Index
import numpy as np
from score import cosine_similarity

class User:
    def __init__(self, id, username, mentions):
        self.id = int(id)
        self.username = username
        self.mentions = mentions

    def add_mention(self, uid):
        if uid not in self.mentions:
            self.mentions[uid] = 0
        self.mentions[uid] += 1

    @staticmethod
    def from_dict(data):
        mentions = {int(user): int(mention) for user, mention in data['MENTIONS'].items()}
        return User(int(data['USERID']), data['USERNAME'], mentions)

    @staticmethod
    def from_json(json_str):
        user_data = json.loads(json_str)
        return User.from_dict(user_data)

    def to_json(self):
        return {
            'USERID' : self.id,
            'USERNAME' : self.username,
            'MENTIONS' : self.mentions}

class UserTweets:
    def __init__(self, user, tweets):
        self.user = user
        self.tweets = tweets
        self.__vector = None

    def add_tweet(self, tweet):
        self.tweets.append(tweet)

    def compute_vector(self, index):
        self.__vector = np.mean([index.get_tf_idf_vector(t.id) for t in self.tweets])

    def get_vector(self):
        return self.__vector

def load_users(file):
    with open(str(file), 'r') as fp:
        for line in fp.readlines():
            file_users = json.loads(line)
    return {int(uid):User.from_dict(user_dict)
                for uid, user_dict in file_users.items()}

def get_user_tweets(users, index):
    user_tweets = {}
    for tweet in index.tweets.values():
        if tweet.user in users:
            user = users[tweet.user]
            if user.id not in user_tweets:
                user_tweets[user.id] = UserTweets(user, [])
            user_tweets[user.id].add_tweet(tweet)
    for u in user_tweets.values():
        u.compute_vector(index)
    return user_tweets

def user_relevance(user1: UserTweets, user2: UserTweets, threshold):
    return cosine_similarity(user1.vector, user2.vector) > threshold