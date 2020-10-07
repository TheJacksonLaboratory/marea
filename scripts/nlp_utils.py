import nltk
from nltk.corpus import stopwords
from os import makedirs
from os.path import abspath


def nltk_setup(data_dir: str) -> None:
    """ Download the minimum of NLTK to make MyLemmatizer work."""
    makedirs(data_dir, exist_ok=True)
    try:
        nltk.download('averaged_perceptron_tagger', download_dir=data_dir, raise_on_error=True)
        nltk.download('punkt', download_dir=data_dir, raise_on_error=True)
        nltk.download('wordnet', download_dir=data_dir, raise_on_error=True)
    except ValueError:
        raise SystemExit('nltk_setup: Error downloading nltk data to {}'.format(data_dir))
    nltk.data.path.append(abspath(data_dir))


def remove_stop_words(phrase: str) -> str:
    """ Remove stop words from input string, return resulting string."""
    word_list = nltk.word_tokenize(phrase)
    return ''.join([w for w in word_list if w not in stopwords.words('english')])