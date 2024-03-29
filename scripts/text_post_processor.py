import click

from my_lemmatizer import MyLemmatizer
from nlp_utils import nltk_setup
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from os.path import join
from string import ascii_lowercase


class TextPostProcessor:
    my_stop_words = set(ascii_lowercase) | \
                    {'also', 'cannot', 'could', 'furthermore', 'however',
                     'may', 'might', 'non', 'thus', 'whose', 'within',
                     'without', 'would'}

    interesting_numbers = {'001', '01', '05', '0', '1', '2', '3', '4', '5', '6',
                           '7', '8', '9', '10', '95', '99', '100'}

    def __init__(self, data_dir: str):
        nltk_setup(data_dir)
        TextPostProcessor.my_stop_words.update(stopwords.words('english'))
        self.lem = MyLemmatizer()
        # lexicon of lemmatized tokens along with words that lemmatize to each
        # token and their counts
        self.lemlex = {}
        # copied from https://github.com/nltk/nltk/issues/1900
        # this tokenizer removes all punctuation symbols, including underscore,
        # whether they occur within a word or between words => any hyphenated
        # word becomes two separate tokens, and any decimal number loses its
        # decimal point and becomes two integers
        self.rt = RegexpTokenizer(r'[^\W_]+|[^\W_\s]+')

    def _build_lemlex(self) -> None:
        """
        Build a lexicon of lemmatized tokens starting from MyLemmatizer's lexicon.
        lemlex is a dictionary with
        key: lemmatized token,
        value: tuple of totalcount, dictionary mapping word to word_count for each
        word that lemmatizes to this token
        """
        for word, (lemmatized, count) in self.lem.lexicon.items():
            if lemmatized in self.lemlex:
                # If lemmatized token has been seen already, add word and its count to
                # the dictionary for this token and update total count for the token
                updated_count = self.lemlex[lemmatized][0] + count
                self.lemlex[lemmatized][1][word] = count
                self.lemlex[lemmatized] = (updated_count, self.lemlex[lemmatized][1])
            else:
                # If the token is new, make an entry for it in the lexicon, initializing
                # the dictionary of words associated with this lemmatized form
                self.lemlex[lemmatized] = (count, {word: count})

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
        stop words and uninteresting numerical tokens. nltk has only lowercase
        stop words on its list. The lowercase_first function handles the
        situation where a stop word appears at the beginning of a sentence.
        I avoided lowercasing the entire token before stop word removal because
        I did not want scientific or medical abbreviations written in capital
        letters to be mistaken for stop words (e.g., ALL for acute lymphocytic
        leukemia or WAS for Wiskott Aldrich syndrome). Lemmatize the remaining
        tokens. The lemmatizer does not change any token that contains uppercase
        letters, so acronyms are preserved. Finally, convert the list of tokens
        to lowercase and glue them back together, separated by spaces.
        :param phrase: input string
        :return:       processed input string
        """
        return ' '.join([self.lem.lemmatize_word(w).lower()
                         for w in map(TextPostProcessor.lowercase_first,
                                      self.rt.tokenize(phrase))
                         if TextPostProcessor._to_keep(w)])

    def report_lexicon(self, outdir: str) -> None:
        """
        Write lexicon to two files, one in alphabetical order and one in
        decreasing order of word frequency. Each line has a lemmatized
        token, its frequency count, and the list of words that map to
        this lemmatized form with their respective frequency counts
        :param outdir:  output directory for writing lexicon files
        :return:        None
        """
        self._build_lemlex()
        with click.open_file(join(outdir, 'lemmatized_alpha.txt'), 'w') as alphafile:
            TextPostProcessor._write_lex_header(alphafile)
            for (lemmatized, (total_count, word_dict)) in sorted(self.lemlex.items()):
                TextPostProcessor._write_lex_line(alphafile, lemmatized, total_count,
                                                  sorted(word_dict.items()))
        with click.open_file(join(outdir, 'lemmatized_freq.txt'), 'w') as freqfile:
            TextPostProcessor._write_lex_header(freqfile)
            # The lamda expression sorts in descending order of frequency, then in
            # ascending alphabetical order among tokens that have the same frequency.
            # Taking the negative of frequency is equivalent to sorting on frequency
            # with reverse=true, but allows the alphabetical sort to be ascending.
            for (lemmatized, (total_count, word_dict)) in sorted(
                    self.lemlex.items(),
                    key=lambda item: (-item[1][0], item[0])):
                TextPostProcessor._write_lex_line(freqfile, lemmatized, total_count,
                                                  sorted(
                                                      word_dict.items(),
                                                      key=lambda item: (-item[1], item[0])))

    @staticmethod
    def _to_keep(token: str) -> bool:
        """
        Decide whether to keep or discard this token: is it a stopword or an uninteresting
        numerical token? Any token that starts with a digit (even if the rest of the
        string includes some letters) is treated as numerical and discarded if it is not
        one of the interesting numbers (defined above as a class variable).
        :param token: string to be examined
        :return:      True if token should be kept, False otherwise.
        """
        if token[0].isnumeric():
            keep = token in TextPostProcessor.interesting_numbers
        else:
            keep = token not in TextPostProcessor.my_stop_words
        return keep

    @staticmethod
    def _write_lex_header(outfile) -> None:
        """
        Write header line to lexicon output file.
        :param outfile: file handle for output
        :return:        None
        """
        outfile.write('{0:<25s}\t{1:>20s}\t{2:<50s}\n'.
                      format('Lemmatized', 'Frequency', 'Words'))

    @staticmethod
    def _write_lex_line(outfile, lemmatized: str, count: int, words: list) -> None:
        """
        Write one line of output for lexicon of lemmatized tokens.
        :param outfile:     file handle for output
        :param lemmatized:  lemmatized token
        :param count:       total count of occurrences of the lemmatized token
        :param words:       list of words that lemmatize to this token, each mapped to
                            its frequency of occurrence
        :return:            None
        """
        outfile.write('{0:<25s}\t{1:>20d}\t'.format(lemmatized, count))
        outfile.write('; '.join(' '.join([word, str(count)]) for (word, count) in words))
        outfile.write('\n')
