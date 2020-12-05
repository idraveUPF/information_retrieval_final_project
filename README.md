# README

In this project we have implemented a search engine for tweets related to the black lives matter movement. We also analized the most frequent words and the different topics inside the movement. We finally implemented a users recommender system. 

# The structure of the repository is: 

  - index.py
  - main.py
  - query.py
  - score.py
  - tweet_stream.py
  - tweet.py
  - user.py
  - utils.py
### Execution

```sh
$ python main.py -index -tweets -K -custom
```
Arguments:
-tweets: tweets json file, 
-index: pickle file with the index, 
-K: number of results per query, 
-custom: use the custom score instead of tf-idf
-diversity: use the diversity score
