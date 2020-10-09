import nltk
import re
from nltk.corpus import stopwords
from os import makedirs
from os.path import abspath


def nltk_setup(data_dir: str) -> None:
    """ Download the minimum of NLTK to lemmatize and remove stop words."""
    makedirs(data_dir, exist_ok=True)
    try:
        nltk.download('averaged_perceptron_tagger', download_dir=data_dir, raise_on_error=True)
        nltk.download('punkt', download_dir=data_dir, raise_on_error=True)
        nltk.download('stopwords', download_dir=data_dir, raise_on_error=True)
        nltk.download('wordnet', download_dir=data_dir, raise_on_error=True)
    except ValueError:
        raise SystemExit('nltk_setup: Error downloading nltk data to {}'.format(data_dir))
    nltk.data.path.append(abspath(data_dir))


def remove_stop_words(phrase: str) -> str:
    """
    Tokenize input string and remove stop words. For any word that begins or
    ends with a hyphen, remove the hyphen. Glue the remaining tokens back
    together, separated by spaces. Note that word_tokenize adds space around
    punctuation, parentheses, and brackets.
    """
    word_list = nltk.word_tokenize(phrase)
    return ' '.join([remove_edge_hyphen(w) for w in word_list
                     if w not in stopwords.words('english')])


def remove_edge_hyphen(token: str) -> str:
    """
    Check whether token begins with a hyphen followed by a letter, or
    ends with a letter followed by a hyphen. If so, remove the hyphen
    and return the rest of the token. Examples:
    -induced -> induced
    anti- -> anti
    """
    m = re.match(r'^-[a-z]', token, re.IGNORECASE)
    if m:
        token = token.lstrip('-')
    m = re.search(r'[a-z]-$', token, re.IGNORECASE)
    if m:
        token = token.rstrip('-')
    return token
