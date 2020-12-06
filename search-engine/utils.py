from nltk import PorterStemmer
from nltk.corpus import stopwords
import re
import math
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

def get_terms(line):
    """
    Preprocess the article text (title + body) removing stop words, stemming,
    transforming in lowercase and return the tokens of the text.

    Argument:
    line -- string (text) to be preprocessed

    Returns:
    line - a list of tokens corresponding to the input text after the preprocessing
    """

    stemming = PorterStemmer()
    stops = set(stopwords.words("english"))
    ## START CODE
    line = line.lower()  ## Transform in lowercase
    line = re.sub(r'http\S+', '', line)
    line = re.sub(r'&amp', '', line)
    line = re.sub(r'\d+', '', line)
    line = re.sub(r'\W', ' ', line)
    line = line.split()  ## Tokenize the text to get a list of terms
    line = [word for word in line if word not in stops]  ##eliminate the stopwords (HINT: use List Comprehension)
    line = [stemming.stem(word)
            for word in line]  ## perform stemming (HINT: use List Comprehension)
    ## END CODE
    return line