from index import Index
from score import rank_tweets, CustomScorer, rank_tweets_diversity
from query import Query
from tweet_stream import OUTPUT_JSON
import argparse

def parse_main_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-index', default=None)
    group.add_argument('-tweets', default=OUTPUT_JSON)
    parser.add_argument('-K', type=int, default=20)
    parser.add_argument('-custom', action='store_true')
    parser.add_argument('-diversity', action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_main_args()

    if args.index != None:
        index = Index.load(args.index)
    else:
        index = Index()
        index.load_json_tweets(args.tweets)

    stop = False
    scorer = None
    if args.custom:
        scorer = CustomScorer()
    ranker = rank_tweets if not args.diversity else rank_tweets_diversity
    while not stop:
        str_query = input('Write a query: ')
        query = Query(str_query)
        for i, tweet in enumerate(ranker(query, index, K=args.K, scorer=scorer)):
            print(i+1, '.\n', '-'*100)
            print(str(tweet))
