import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

from gensim.models import Word2Vec
import sqldict

import spacy

import pdb

class TokenVectorizer(object):
    def __init__(self, model=None):
        self.stops = set(stopwords.words('english'))

        path = '/Users/dpmorg_mac/dpm_gdrive/insight/polibot/depedencies/'
        if model is None:
            self.model = sqldict.SqlDict(path+"GoogleNews-vectors.db")
        else:
            pretrained = path+'GoogleNews-vectors-negative300.bin.gz'
            self.model = Word2Vec.load_word2vec_format(pretrained, binary=True)

        self.nlp = spacy.load('en')

    def tokenize_tosentence(self, text):
        ''' Seperates text into the individual words and stems.'''
        tokens = self.nlp(text, parse=True)

        '''
        sentences = []
        for s in tokens.sents:
            print(''.join(tok.string for tok in tokens))
        '''
        sentences = []
        for sent in tokens.sents:
            try:
                sentences.append(str(sent))
            except:
                continue

        return sentences

    def tokenize_full(self,sentence):

        # Split into word tokens
        try:
            tokens = self.tokenize_towords(sentence)
        except:
            return None

        # Remove stop words
        try:
            tokens_nostops = self.remove_stops(tokens)
        except:
            return None

        return tokens_nostops

    def tokenize_towords(self, text):
        ''' Seperates text into the individual words and stems.'''
        #clean_text = re.sub("[^a-zA-Z]"," ", text)
        #words = clean_text.lower().split()
        tokens = self.nlp(text, parse=True)

        return [t for t in tokens if t.is_alpha==True]

    def remove_stops(self, tokens):
        ''' Remove stop words from the list; i.e. words that don't
            matter (is, the, you, etc.)
        '''

        return [t for t in tokens if t.is_stop==False]

    def make_vector(self, wordString):
        ''' @pre: unique(vectorIndex) '''
        vector = []
        for word in wordString:
            try:
                vector.append(self.model[word])
            except:
                print("Missing word %s" %(str(word)))

        return vector
