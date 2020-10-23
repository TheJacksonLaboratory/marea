import nltk
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
