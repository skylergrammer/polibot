import markovify
import nltk
import pdb

class POSifiedText(markovify.Text):
    def word_split(self, sentence):
        words = re.split(self.word_split_pattern, sentence)
        words = [ "::".join(tag) for tag in nltk.pos_tag(words) ]
        return words

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence

class MarkovChain(object):
    def __init__(self, text):
        self.model = markovify.Text(text, state_size=3)

    def generate_sentences(self, num_sent=100):

        sorin_sentences = []
        for ns in range(num_sent):
            sorin_sentences.append(
                    self.model.make_sentence(tries=100))

        return sorin_sentences
