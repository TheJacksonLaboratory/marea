import nltk
import re
from nlp_utils import nltk_setup
from nltk.corpus import stopwords
from string import ascii_lowercase, punctuation

PRE_HYPHEN = re.compile(r'^-[a-z]', re.IGNORECASE)
POST_HYPHEN = re.compile(r'[a-z]-$', re.IGNORECASE)


class TextPostProcessor:

    my_stop_words = set(ascii_lowercase) | set(punctuation) | \
                    {"'s", 'also', 'could', 'furthermore', 'however', 'may',
                     'might', 'thus', 'whose', 'within', 'without', 'would'}

    def __init__(self, data_dir: str):
        nltk_setup(data_dir)
        TextPostProcessor.my_stop_words.update(stopwords.words('english'))

    @staticmethod
    def lowercase_first(token: str) -> str:
        """
        Convert first character of input token to lowercase.
        :param token: input string
        :return:      string identical to input except first char is lowercase
        """
        return token[:1].lower() + token[1:]

    @classmethod
    def remove_stop_words(cls, phrase: str) -> str:
        """
        Tokenize input string and remove stop words. For any word that begins
        or ends with a hyphen, remove the hyphen before checking it against
        the stop words. Glue the remaining tokens back together, separated by
        spaces. Note that word_tokenize adds space around punctuation,
        parentheses, and brackets. nltk has only lowercase stop words on its
        list. The lowercase_first function handles the situation where a stop
        word appears at the beginning of a sentence. I did not want to make
        the entire input lowercase because then scientific or medical
        abbreviations written in capital letters could be mistaken for stop
        words (e.g., ALL for acute lymphocytic leukemia or WAS for Wiskott
        Aldrich syndrome).
        """
        word_list = nltk.word_tokenize(phrase)
        return ' '.join([w for w in map(cls.remove_edge_hyphen, word_list)
                         if cls.lowercase_first(w) not in
                         TextPostProcessor.my_stop_words])

    @classmethod
    def remove_edge_hyphen(cls, token: str) -> str:
        """
        Check whether token begins with a hyphen followed by a letter, or
        ends with a letter followed by a hyphen. If so, remove the hyphen
        and return the rest of the token. Examples:
        -induced -> induced
        anti- -> anti
        """
        if PRE_HYPHEN.match(token):
            token = token.lstrip('-')
        if POST_HYPHEN.search(token):
            token = token.rstrip('-')
        return token
