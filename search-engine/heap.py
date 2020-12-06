from tweet import Tweet
from utils import cosine_similarity
from heapq import heappush, heappop, heapify

class DiversityHeap:
    def __init__(self, scorer, query):
        self.query = query
        self.scorer = scorer
        self.ranking = []   #heap containing ranking
        self.div_rank = []
        self.vectors = {}   #vectors of tweets in ranking
        self.scores = {}    #scores of tweets given scorer
        self.div = {}       # diversity of tweets wrt other tweets in ranking
        self.total_div = {} #total diversity of tweets wrt others in ranking

    def push(self, tweet: Tweet):
        tid = tweet.id
        vector = self.scorer.get_tweet_vector(tweet)
        self.vectors[tid] = vector
        score = self.scorer.score(tweet, self.query)
        self.scores[tid] = score
        total = 0
        div = {}
        for t, tdiv in self.div.items():
            d = cosine_similarity(vector, self.vectors[t])
            div[t] = d
            tdiv[tid] = d
            total += d
        self.div[tid] = div
        self.total_div[tid] = total
        heappush(self.ranking, (score, tid))

    def pop(self):
        to_pop = min((self.scores[t]+self.total_div[t]/len(self), t) for t in self.scores)[1]
        div = self.div[to_pop]
        self.total_div.pop(to_pop)
        for t in self.total_div:
            self.total_div[t] -= div[t]
        self.scores.pop(to_pop)
        self.div.pop(to_pop)
        self.vectors.pop(to_pop)
        self.ranking = [(score, t) for t, score in self.scores.items()]
        heapify(self.ranking)
        return to_pop

    def pushpop(self, tweet: Tweet):
        self.push(tweet)
        return self.pop()

    def __len__(self):
        return len(self.scores)

    def __iter__(self):
        return iter(self.ranking)