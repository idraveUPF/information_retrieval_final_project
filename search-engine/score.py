from tweet import Tweet
import math
from heapq import heappush, heappushpop, heappop
from gensim.models import Word2Vec
import numpy as np
from query import Query

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
    print(total, sum_a, sum_b)
    return total / (sum_a * sum_b)

class TfIdfScorer:
    def __init__(self):
        pass
    def score(self, tweet: Tweet, query, index, normalize=True):
        tweet_v = []
        query_v = []
        tweet_tf = index.get_tf(query, tweet.id)
        query_tf = query.get_tf()
        idfs = index.get_idf(query)
        for i in range(len(query_tf)):
            tweet_v.append(tweet_tf[i] * idfs[i])
            query_v.append(query_tf[i] * idfs[i])
        print(tweet_tf)
        print(query_tf)
        return cosine_similarity(tweet_v, query_v, norm_a=normalize, norm_b=normalize) # assume get_tf normalizes

class CustomScorer:
    W_TFIDF = .5
    W_FAV = .25
    W_RT = .25
    def __init__(self):
        pass

    def score(self, tweet: Tweet, query, index, normalize=True):
        tfidf = TfIdfScorer().score(tweet, query, index, normalize=normalize)
        tweet.retweets # fav / max(fav), log(fav) / log(max(fav))
        max_fav = index.get_max_fav()
        max_rt = index.get_max_rt()
        fav_score = math.log(tweet.likes)/math.log(max_fav) # TQM
        rt_score = math.log(tweet.retweets)/math.log(max_rt)
        score = tfidf * CustomScorer.W_TFIDF + \
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

    def score(self, tweet, query: Query, index):
        tweet_v = np.mean([self.get_vector(token) for token in tweet.tokens()], axis=0)
        query_v = np.mean([self.get_vector(token) for token in query.get_terms()], axis=0)
        return cosine_similarity(tweet_v, query_v)

def rank_tweets(query: Query, index, K=20, scorer=None, log=False):
    scorer = scorer if scorer is not None else TfIdfScorer()
    heap = []
    for tweet in index.get_tweets(query):
        score = scorer.score(tweet, query, index)
        if len(heap) < K:
            heappush(heap, (score, tweet.id))
        else:
            heappushpop(heap, (score, tweet.id))
    if log:
        heap2 = list(heap)
        ranking_scores = [heappop(heap2) for _ in range(len(heap2))]
        ranking_scores.reverse()
        for score, tweet in ranking_scores:
            print(score, index.tweets[tweet].text)
    ranking = [heappop(heap)[1] for _ in range(len(heap))]
    ranking.reverse()

    return [index.tweets[tid] for tid in ranking]

