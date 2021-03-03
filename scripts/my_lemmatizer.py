import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

# Most of this class definition is copied from
# https://www.machinelearningplus.com/nlp/lemmatization-examples-python/.


class MyLemmatizer(WordNetLemmatizer):
    """
    MyLemmatizer is a regular WordNetLemmatizer that can process not just a
    single word but a sequence of words. It remembers words it has seen before
    to avoid recalculating the same string multiple times. It also tracks word
    frequency and can return a lexicon of words it has lemmatized.
    """

    def __init__(self):
        self.lexicon = {}
        super().__init__()

    @staticmethod
    def get_wordnet_pos(word: str):
        """
        Map Penn treebank POS tag to wordnet part of speech tags.
        Default part of speech for wordnet lemmatizer is noun.
        """
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN)

    def lemmatize_word(self, word) -> str:
        """
        Lemmatize input word, update count for that word in lexicon.
        :param word:  String to lemmatize with WordNet lemmatizer.
        :return:      String of lemmatized form (may be identical to input)
        """
        if word in self.lexicon:
            # if word has been seen already, pull lemmatized form from dictionary
            # and increment the number of times that word has been seen
            lemmatized, count = self.lexicon[word]
            self.lexicon[word] = lemmatized, count + 1
        else:
            # if the word is new, calculate its lemmatized form and record it in
            # dictionary
            lemmatized = super().lemmatize(word, self.get_wordnet_pos(word))
            self.lexicon[word] = lemmatized, 1
        return lemmatized

    def lemmatize_seq(self, seq: str) -> str:
        """
        Lemmatize a sequence of words.
        :param seq: String of one or more words
        :return:    String of lemmatized form for each word in input phrase
        """
        word_list = nltk.word_tokenize(seq)
        lemmatized_output = ' '.join([self.lemmatize_word(w) for w in word_list])
        return lemmatized_output

    @property
    def lexicon(self):
        return self.__lexicon

    @lexicon.setter
    def lexicon(self, value):
        self.__lexicon = value
