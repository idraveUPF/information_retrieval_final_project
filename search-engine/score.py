from .tweet import Tweet
import math
from heapq import heappush, heappushpop, heappop
from gensim.models import Word2Vec
import numpy as np

def cosine_similarity(a, b, norm_a=True, norm_b=True):
    total = 0
    sum_a = 0 if norm_a else 1.0
    sum_b = 0 if norm_b else 1.0
    for x, y in zip(a, b):
        total += x * y
        if norm_a:
            sum_a += x * x
        if norm_b:
            sum_b += y * y
    if norm_a:
        sum_a = math.sqrt(sum_a)
    if norm_b:
        sum_b = math.sqrt(sum_b)
    return total / (sum_a * sum_b)

class TfIdfScorer:
    def __init__(self):
        pass
    def score(self, tweet: Tweet, query, index, normalize=True):
        tweet_v = []
        query_v = []
        for token, query_tf in query.get_tf(normalize=normalize):
            tweet_tf = index.get_tf(token, tweet)
            if tweet_tf > 0:
                token_idf = index.get_idf(token)
                tweet_v.append(tweet_tf * token_idf)
                query_v.append(query_tf * token_idf)
        return cosine_similarity(tweet_v, query_v, norm_a=normalize, norm_b=False) # assume get_tf normalizes

class CustomScorer:
    W_TFIDF = .5
    W_FAV = .25
    W_RT = .25
    def __init__(self):
        pass

    def score(self, tweet: Tweet, query, index, normalize=True):
        cosine = TfIdfScorer().score(tweet, query, index, normalize=normalize)
        fav_score = index.get_fav(tweet) # TQM
        rt_score = index.get_rt(tweet)
        score = cosine * CustomScorer.W_TFIDF + \
                    fav_score * CustomScorer.W_FAV + \
                    rt_score * CustomScorer.W_RT
        return score

class Word2VecScorer:
    def __init__(self, sentences=[], size=100, window=5, min_count=1, epochs=5):
        self.model = Word2Vec(sentences, size=size, window=window, min_count=min_count, iter=epochs)
    def save(self, path):
        self.model.save(path)
    @staticmethod
    def load(self, path):
        word2vec = Word2VecScorer()
        word2vec.model = Word2Vec.load(path)
        return word2vec
    def get_vector(self, word):
        if word not in self.model.wv.vocab:
            return np.random.uniform(size=len(self.model.vector_size))
        return self.model.wv[word]
    def score(self, tweet, query, index):
        tweet_v = np.mean([self.get_vector(token) for token in tweet.tokens()], axis=0)
        query_v = np.mean([self.get_vector(token) for token in query.tokens()], axis=0)
        return cosine_similarity(tweet_v, query_v)

def rank_tweets(query, index, K=20, scorer=None):
    scorer = scorer if scorer is not None else TfIdfScorer()
    heap = []
    for tweet in index.get_tweets(query):
        score = scorer.score(tweet, query, index)
        if len(heap) < K:
            heappush(heap, (score, tweet.id))
        else:
            heappushpop(heap, (score, tweet.id))
    ranking = [heappop(heap)[1] for _ in range(len(heap))].reverse()
    return [index.get_from_id(tid) for tid in ranking]

