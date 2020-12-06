from index import Index
from score import rank_tweets, CustomScorer, rank_tweets_diversity, Word2VecScorer
from query import Query
from pathlib import Path
import argparse
import csv

DEFAULT_TWEETS = Path(__file__).parent.parent/'res'/'merge_tweets_wusers.json'

def parse_main_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-index', default=None)
    group.add_argument('-tweets', default=DEFAULT_TWEETS)
    parser.add_argument('-K', type=int, default=20)
    parser.add_argument('-out', default=None)
    parser.add_argument('-w2v', action='store_true')
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
    if args.w2v:
        scorer = Word2VecScorer(index.tweets.values())
    if args.custom:
        scorer = CustomScorer(index)

    ranker = rank_tweets if not args.diversity else rank_tweets_diversity

    while not stop:
        str_query = input('Write a query: ')
        query = Query(str_query)
        output = []
        for i, tweet in enumerate(ranker(query, index, K=args.K, scorer=scorer)):
            print(i+1, '.\n', '-'*100)
            print(str(tweet))
            output.append(tweet)
        if args.out != None:
            with open(args.out, 'at') as out_file:
                tsv_writer = csv.writer(out_file, delimiter='\t')
                tsv_writer.writerow(['query', str_query])
                for tweet in output:
                    tsv_writer.writerow(tweet.row_data())
