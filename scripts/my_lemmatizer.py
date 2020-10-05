import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

# Most of this class definition is copied from
# https://www.machinelearningplus.com/nlp/lemmatization-examples-python/.


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


class MyLemmatizer(WordNetLemmatizer):
    """
    MyLemmatizer is a regular WordNetLemmatizer that can process not just a
    single word but a sequence of words.
    """

    def __init__(self):
        super().__init__()

    def lemmatize_word(self, word) -> str:
        return super().lemmatize(word, get_wordnet_pos(word))

    def lemmatize_seq(self, seq: str) -> str:
        word_list = nltk.word_tokenize(seq)
        lemmatized_output = ' '.join([self.lemmatize_word(w) for w in word_list])
        return lemmatized_output
