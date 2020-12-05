#import scrapping.py
import math
import json
from collections import defaultdict
import numpy as np
import pickle

from tweet import Tweet
from array import array

class Index:

    def __init__(self):
        self.index= None # term --> tweet
        self.tf = None
        self.df = None
        self.tweets = {}
        self.term_id = {}
        self.max_fav = 0
        self.max_rt = 0

    def load_json_tweets(self, file):
        with open(file, 'r') as fp:
            self.create_index(fp.readlines())

    def save(self, path):
        with open(path, 'wb') as fp:
            pickle.dump(self, fp)

    @staticmethod
    def load(path):
        with open(path, 'rb') as fp:
            index = pickle.load(fp)
        return index

    def create_index(self, lines):
        """
        Impleent the inverted index
        
        Argument:
        lines -- collection of tweets
        
        Returns:
        index - the inverted index (implemented through a python dictionary) containing terms as keys and the corresponding 
        list of tweets these keys appears in (and the positions) as values.
        """


        index=defaultdict(list)
        tf = defaultdict(dict)
        df = defaultdict(int)

        for line in lines: # Remember, lines contain all tweets, each line is a tweet
            tweet_json = json.loads(line)
            tweet = Tweet(
                tweet_json['ID'], tweet_json['Tweet_text'], tweet_json['UserId'],
                tweet_json['Date'], tweet_json['URL'], tweet_json['Hashtags'],
                tweet_json['Likes'], tweet_json['Number_Retweets'], tweet_json['terms']
            )
            if tweet.id in self.tweets:
                continue
            self.tweets[tweet.id] = tweet
            tweet_id = tweet.id #tweet id
            terms = tweet.terms #page_title + page_text
            self.max_fav = max(self.max_fav, tweet.likes)
            self.max_rt = max(self.max_rt, tweet.retweets)
            #title = line_arr[1]            
            #titleIndex[page_id]=title  ## we do not need to apply get terms to title because it used only to print titles and not in the index
            
            ## ===============================================================        
            ## create the index for the current doc and store it in termdictPage
            ## termdictPage ==> { ‘term1’: [currentdoc, [list of positions]], ...,‘termn’: [currentdoc, [list of positions]]}
            
            ## Example: if the curr_doc has id 1 and his text is 
            ## "web retrieval information retrieval":
            
            ## termdictPage ==> { ‘web’: [1, [0]], ‘retrieval’: [1, [1,3]], ‘information’: [1, [2]]}
            
            ## the term ‘web’ appears in document 1 in positions 0, 
            ## the term ‘retrieval’ appears in document 1 in positions 1 and 3
            ## ===============================================================
            
            termdictTweets={}

            for position, term in enumerate(terms): # terms contains page_title + page_text. Loop over all terms
                if term not in self.term_id:
                    self.term_id[term] = len(self.term_id)
                try:
                    # if the term is already in the index for the current page (termdictPage)
                    # append the position to the corrisponding list
                    
            ## START CODE
                    termdictTweets[term][1].append(position)  
                except:
                    # Add the new term as dict key and initialize the array of positions and add the position
                    termdictTweets[term]=[tweet_id, array('I',[position])] #'I' indicates unsigned int (int in python)
                
            #merge the current page index with the main index
            for termpage, postingpage in termdictTweets.items():
                index[termpage].append(postingpage)

            # normalize term frequencies
            # Compute the denominator to normalize term frequencies (formula 2 above)
            # norm is the same for all terms of a document.
            norm = 0
            for term, posting in termdictTweets.items():
                # posting is a list containing doc_id and the list of positions for current term in current document:
                # posting ==> [currentdoc, [list of positions]]
                # you can use it to inferr the frequency of current term.
                norm += len(posting[1]) ** 2
            norm = math.sqrt(norm)

            # calculate the tf(dividing the term frequency by the above computed norm) and df weights
            for term, posting in termdictTweets.items():
                # append the tf for current term (tf = term frequency in current doc/norm)
                tf[term][posting[0]] = np.round(len(posting[1]) / norm, 4) ## SEE formula (1) above
                # increment the document frequency of current term (number of documents containing the current term)
                df[term] += 1  # increment df for current term
            ## END CODE                    
        self.index = index
        self.tf = tf
        self.df = df

    #Given a query (set of words) and and index return the idf of that query
    def get_idf(self, query):
        N=len(self.tweets)
        idf=[]
        query=query.get_terms()
        for term in query:
            df=self.df[term]
            idf.append(math.log(N/df))
        return idf

    #Given a query (set of words) and and index return the total tf of that query 
    def get_tf(self, query, tweet_id):
        query=query.get_terms()
        global_tf_list=[]
        term_list=[]
        for term in query:
            term_list.append(self.tf[term][tweet_id])
        return term_list

    def get_tf_idf_vector(self, tweet_id):
        vector = np.zeros(len(self.index))
        N = len(self.tweets)
        total = 0
        for term in self.tweets[tweet_id].terms:
            tf = self.tf[term].get(tweet_id, 0)
            df = self.df[term]
            tf_idf = tf * math.log(N / df)
            vector[self.term_id[term]] = tf_idf
        norm = np.linalg.norm(vector)
        if norm == 0:
            return None
        return vector / norm

    def get_all_tf_idf(self):
        vectors = np.array([])
        for tweet in self.tweets:
            v = self.get_tf_idf_vector(tweet)
            if isinstance(v, np.ndarray):
                vectors = np.vstack((vectors, v))
            if len(vectors) % 1000 == 0:
                print(len(vectors))
        return vectors

    #Given a query (set of words) return all the tweets containing the query
    def get_tweets(self, query):
        query=query.get_terms()
        list_tweets=set()
        for term in query:
            ## START DODE
            try:
                # store in termDocs the ids of the docs that contain "term"
                termTweets=[posting[0] for posting in self.index[term]]
                # docs = docs Union termDocs
                if len(list_tweets) == 0:
                    list_tweets = list_tweets.union(termTweets)
                else:
                    list_tweets = list_tweets.intersection(termTweets)
            except:
                #term is not in index
                pass
        list_tweets=list(list_tweets)

        tweets_query = [self.tweets[tid] for tid in list_tweets] #asssuming index of tweets is id
        #list of tweets ids
        return tweets_query

    #Given a query (set of words) return the tweets number of tweets containing the query
    def get_num_tweets(self,query):

        num_tweets=len(self.get_tweets(query))

        return num_tweets

    def get_max_fav(self):
        return self.max_fav

    def get_max_rt(self):
        return self.max_rt
