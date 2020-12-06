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
    return total / (sum_a * sum_b)

class TfIdfScorer:
    def __init__(self, index):
        self.index = index

    def get_tweet_vector(self, tweet):
        return self.index.get_tf_idf_vector(tweet.id)

    def score(self, tweet: Tweet, query, normalize=True):
        tweet_v = []
        query_v = []
        tweet_tf = self.index.get_tf(query, tweet.id)
        query_tf = query.get_tf()
        idfs = self.index.get_idf(query)
        for i in range(len(query_tf)):
            tweet_v.append(tweet_tf[i] * idfs[i])
            query_v.append(query_tf[i] * idfs[i])
        return cosine_similarity(tweet_v, query_v, norm_a=normalize, norm_b=normalize) # assume get_tf normalizes

class CustomScorer:
    W_TFIDF = .5
    W_FAV = .25
    W_RT = .25
    def __init__(self, index):
        self.index = index

    def get_tweet_vector(self, tweet):
        return self.index.get_tf_idf_vector(tweet.id)

    def score(self, tweet: Tweet, query, normalize=True):
        tfidf = TfIdfScorer(self.index).score(tweet, query, normalize=normalize)
        max_fav = self.index.get_max_fav()
        max_rt = self.index.get_max_rt()
        fav_score = math.log(tweet.likes + 1)/(math.log(max_fav + 1) + 1)# TQM
        rt_score = math.log(tweet.retweets + 1)/(math.log(max_rt + 1) + 1)
        score = tfidf * CustomScorer.W_TFIDF + \
                    fav_score * CustomScorer.W_FAV + \
                    rt_score * CustomScorer.W_RT
        return score

class Word2VecScorer:
    def __init__(self, tweets=[], size=100, window=5, min_count=1, epochs=5):
        sentences = [tweet.get_terms() for tweet in tweets]
        self.model = Word2Vec(sentences, size=size, window=window, min_count=min_count, iter=epochs)

    def save(self, path):
        self.model.save(path)

    @staticmethod
    def load(self, path):
        word2vec = Word2VecScorer()
        word2vec.model = Word2Vec.load(path)
        return word2vec

    def get_tweet_vector(self, tweet):
        if len(tweet.get_terms()) == 0:
            return np.zeros(self.model.vector_size)
        return np.mean([self.get_vector(token) for token in tweet.get_terms()], axis=0)

    def get_vector(self, word):
        if word not in self.model.wv.vocab:
            return np.random.uniform(size=len(self.model.vector_size))
        return self.model.wv[word]

    def score(self, tweet, query: Query):
        tweet_v = np.mean([self.get_vector(token) for token in tweet.tokens()], axis=0)
        query_v = np.mean([self.get_vector(token) for token in query.get_terms()], axis=0)
        return cosine_similarity(tweet_v, query_v)

class DiversityScore:
    W_SCORE = 0.8
    W_DIV = 0.2
    def __init__(self, base_score):
        self.base_score = base_score

    def get_diversity(self, tweet, index, ranking):
        is_in = tweet.id in {id for _, id in ranking}
        count = (len(ranking) - (1 if is_in else 0))
        if count == 0:
            return 0
        v1 = index.get_tf_idf_vector(tweet.id)
        total = 0
        for _, t in ranking:
            total += cosine_similarity(v1, index.get_tf_idf_vector(t))
        return 1 - (total / count) # if tweet is in ranking, we take mean over len(ranking)-1, otherwise, over all len(ranking)

    def score(self, tweet, query: Query, index, ranking):
        score = self.base_score.score(tweet, query, index)
        diversity = self.get_diversity(tweet, index, ranking)
        return score * DiversityScore.W_SCORE + diversity * DiversityScore.W_DIV

def rank_tweets(query: Query, index, K=20, scorer=None, log=False):
    scorer = scorer if scorer is not None else TfIdfScorer(index)
    heap = []
    for tweet in index.get_tweets(query):
        score = scorer.score(tweet, query)
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

def rank_tweets_diversity(query: Query, index, K=20, scorer=None, log=False):

    scorer = scorer if scorer is not None else TfIdfScorer(index)
    heap = []
    div_score = DiversityScore(scorer)

    def recompute(heap):
        new_heap = []
        for _, t_id in heap:
            new_score = div_score.score(index.tweets[t_id], query, heap)
            heappush(new_heap, (new_score, t_id))
        return new_heap

    for tweet in index.get_tweets(query):
        score = div_score.score(tweet, query, index, heap)
        if len(heap) < K:
            heappush(heap, (score, tweet.id))
            heap = recompute(heap)
        else:
            t_out = heappushpop(heap, (score, tweet.id))
            if t_out != tweet.id:
                heap = recompute(heap)
    if log:
        heap2 = list(heap)
        ranking_scores = [heappop(heap2) for _ in range(len(heap2))]
        ranking_scores.reverse()
        for score, tweet in ranking_scores:
            print(score, index.tweets[tweet].text)
    ranking = [heappop(heap)[1] for _ in range(len(heap))]
    ranking.reverse()

    return [index.tweets[tid] for tid in ranking]