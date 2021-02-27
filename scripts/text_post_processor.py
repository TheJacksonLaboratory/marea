import click

from my_lemmatizer import MyLemmatizer
from nlp_utils import nltk_setup
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from os.path import join
from string import ascii_lowercase


class TextPostProcessor:

    # my_stop_words = set(ascii_lowercase) | set(punctuation) | \
    #                 {"'s", 'also', 'could', 'furthermore', 'however', 'may',
    my_stop_words = set(ascii_lowercase) | \
                    {'also', 'cannot', 'could', 'furthermore', 'however',
                     'may',  'might', 'thus', 'whose', 'within', 'without',
                     'would'}

    def __init__(self, data_dir: str):
        nltk_setup(data_dir)
        TextPostProcessor.my_stop_words.update(stopwords.words('english'))
        self.lem = MyLemmatizer()
        # copied from https://github.com/nltk/nltk/issues/1900
        # this tokenizer removes all punctuation symbols, including underscore,
        # whether they occur within a word or between words => hyphenated
        # words become two separate tokens
        self.rt = RegexpTokenizer(r'[^\W_]+|[^\W_\s]+')

    @staticmethod
    def lowercase_first(token: str) -> str:
        """
        Convert first character of input token to lowercase.
        :param token: input string
        :return:      string identical to input except first char is lowercase
        """
        return token[:1].lower() + token[1:]

    def process_phrase(self, phrase: str) -> str:
        """
        Tokenize input string, which eliminates punctuation symbols. Remove
        stop words. nltk has only lowercase stop words on its list. The
        lowercase_first function handles the situation where a stop word
        appears at the beginning of a sentence. I avoided lowercasing the
        entire token before stop word removal because I did not want scientific
        or medical abbreviations written in capital letters to be mistaken for
        stop words (e.g., ALL for acute lymphocytic leukemia or WAS for Wiskott
        Aldrich syndrome). Lemmatize the remaining tokens. The lemmatizer does
        not change any token that starts with an uppercase letter, so acronyms
        are preserved. Finally, convert the list of tokens to lowercase and
        glue them back together, separated by spaces.
        """
        word_list = self.rt.tokenize(phrase)
        word_map = map(TextPostProcessor.lowercase_first, word_list)
        return ' '.join([self.lem.lemmatize_word(w).lower()
                         for w in word_map
                         if w not in TextPostProcessor.my_stop_words])

    def report_lexicon(self, outdir: str) -> None:
        """
        Writes lexicon to two files, one in alphabetical order and one in
        decreasing order of word frequency. Each line has one word, its
        lemmatized form, and its frequency count.
        :param outdir:  output directory for writing lexicon files
        :return:        None
        """
        with click.open_file(join(outdir, 'alphabetical.txt'), 'w') as alphafile:
            for word, (lemmatized, count) in sorted(self.lem.lexicon.items()):
                alphafile.write('{0:<20s}\t{1:<20s}\t{2:>9s}\n'.
                                format('Word', 'Lemmatized', 'Frequency'))
                alphafile.write('{0:<20s}\t{1:<20s}\t{2:>9d}\n'.
                                format(word, lemmatized, count))
        with click.open_file(join(outdir, 'wordfreq.txt'), 'w') as freqfile:
            for word, (lemmatized, count) in sorted(self.lem.lexicon.items(),
                                                    reverse=True,
                                                    key=lambda item: item[1][1]):
                freqfile.write('{0:<20s}\t{1:<20s}\t{2:>9s}\n'.
                               format('Word', 'Lemmatized', 'Frequency'))
                freqfile.write('{0:<20s}\t{1:<20s}\t{2:>9d}\n'.
                               format(word, lemmatized, count))
