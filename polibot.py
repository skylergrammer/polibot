import numpy as np
import pdb, time, datetime

from token_vectorizer import TokenVectorizer
from connect_to_db import ConnectToDB
from markov_chain import MarkovChain

class PoliBot(object):
    def __init__(self, candidate, ):
        """ Prepare the bot for the input candidate."""
        # Connect to the SQL database
        self.DB = ConnectToDB()
        self.corpus_table = 'corpus_table'
        self.question_table = 'question_table'
        self.response_table = 'response_table'

        # Save candidate and get candidate corpus
        self.candidate = candidate.lower()
        self.corpus = self.get_corpus()

        # Initialize the vectorizer
        self.TV = TokenVectorizer()
        # Initialize the markov chain
        self.sorin = MarkovChain(self.corpus)

        # Log dictionary for questions and responses
        self.idnum = 0

    def ask_question(self, question=None):
        ts = time.time()
        self.date = int(datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d'))
        self.time = int(datetime.datetime.fromtimestamp(ts).strftime('%H%M%S'))

        self.ID = str(self.idnum)+'_'+str(ts)
        self.idnum+=1

        try:
            tokens = self.TV.tokenize_full(question)
        except:
            tokens = []

        try:
            word_string = [str(t) for t in tokens]
        except:
            word_string = ""

        try:
            tokens_vect = self.TV.make_vector(word_string)
        except:
            tokens_vect=[]

        if len(tokens_vect) > 1:
            question_vect = sum(tokens_vect)/len(tokens_vect)
        else:
            question_vect = tokens_vect

        if len(question_vect)==1:
            self.question_vect = question_vect[0]
        else:
            self.question_vect = question_vect

        self.question_log = {
                    'question_id':[self.ID],
                    'question_date':[self.date],
                    'question_time':[self.time],
                    'question_sent':[question],
                    'question_tokens':[tokens]}

        self.response_log = {
                    'response_id':[self.ID],
                    'response_date':[self.date],
                    'response_time':[self.time],
                    'response_candidate':[self.candidate],
                    'response_sent':[],
                    'response_tokens':[],
                    'cosine_sim':[0],
                    'question_id':[self.question_log['question_id'][0]]
                    }

        # We want a new response dictionary for each question asked.
        self.response_dict = {}
        self.responseIDcounter = 0
        self.responseLOOPcounter = 0

    def response(self, num_sent=100, tries=10, save_to_db=False):
        generated_sentences = self.sorin.generate_sentences(num_sent=num_sent)

        cosine_sims = [0]
        all_tokens = []
        for i, sent in enumerate(generated_sentences):
            if sent is None:
                continue
            else:
                tokens = self.TV.tokenize_full(sent)
                if tokens is None:
                    continue
                else:
                    word_string = [str(t) for t in tokens]
                    tokens_vect = self.TV.make_vector(word_string)

                if len(tokens_vect) > 1:
                    response_vect = sum(tokens_vect)/len(tokens_vect)
                else:
                    response_vect = tokens_vect

            # Cosine similarity
            try:
                cosine_sim_0 = cosine(response_vect,self.question_vect)
            except:
                continue

            if cosine_sim_0 > np.max(cosine_sims):
                self.response_log['response_sent'] = [sent]
                self.response_log['response_tokens'] = [tokens]
                self.response_log['cosine_sim'] = [cosine_sim_0]

                cosine_sims.append(cosine_sim_0)
                all_tokens.append(tokens)
            else:
                cosine_sims.append(cosine_sim_0)
                all_tokens.append(tokens)

        if (self.responseLOOPcounter < tries) and (self.response_log['cosine_sim'][0] < 0.70):
            self.responseLOOPcounter+=1
            self.response(num_sent=num_sent, tries=tries)
        else:
            self.response_log['cosine_sim_dist'] = \
                    [(np.mean(cosine_sims),np.std(cosine_sims))]

            if save_to_db:
                self.DB.save_to_db(self.question_table, self.question_log)
                self.DB.save_to_db(self.response_table, self.response_log)
            else:
                print("Not saving to db")

        return self.response_log['response_sent'][0]

    def get_corpus(self):

        return self.DB.pull_candidate_corpus(self.corpus_table, self.candidate)
        #documentList['Sanders'] = []
        #parsed_text = parser(self.candidate, documentList[self.candidate])
        #self.corpus = parsed_text.speaker_dict[self.candidate.lower()]

def cosine(vector1, vector2):
    """ related documents j and q are in the concept space by comparing the vectors :
            cosine  = ( V1 * V2 ) / ||V1|| x ||V2|| """
    return float(np.dot(vector1,vector2) /
                (np.linalg.norm(vector1) * np.linalg.norm(vector2)))
