import urllib
from bs4 import BeautifulSoup as BS
import re
import pandas as pd
import pdb
from token_vectorizer import TokenVectorizer
from connect_to_db import ConnectToDB
import time

"""
Usage notes:
    1. fetch the htmltext from the given link
    2. clean the html text of html code
    3. split the document into speaker and speaker_text
    3a. for press releases, this will be only one speaker usually
    4. put the data in a pandas dataframe to then be stored in the sql database
    4a. corpus_ID -- debate_date_line-of-document
        link - link to documennt
        type - debate, speech, interview
        date - time of occurence
        speaker - speaker name
        speaker_text - speaker text
        line_of_document -
    4b. for each line of speaker_text:
        unique_token_id = token_date
        token = the token
        unique_text_ID = question_ID, response_ID, or corpus_ID where token was mentioned
"""

class BuildSaveCorpus(object):
    def __init__(self):
        # Get the html links
        self.get_html_links()
        # Tokenizer!
        self.TV = TokenVectorizer()
        #
        self.DB = ConnectToDB()
        self.table_name = 'corpus_table'

    def build_corpus(self):

        for key, vals in self.html_links.items():

            if 'speech' in key:
                key_speaker = key.split('_')[1]
                doc_type = key.split('_')[0]
            else:
                doc_type = key

            line_of_doc_cter = 0
            for html_link in vals:
                html_text = self.fetch_data(html_link)
                speakers, speakers_text = self.clean_html(html_text)

                if len(speakers)==0:
                    speakers = [str(key_speaker)]*len(speakers_text)

                for speaker, speaker_text in zip(speakers, speakers_text):
                    sentences = self.TV.tokenize_tosentence(speaker_text)

                    for s in sentences:
                        corpus_ID = "_".join([str(doc_type),
                                             str(self.doc_date),
                                             str(line_of_doc_cter)])

                        html_link_dict = {
                                "corpus_id": [corpus_ID],
                                "link": [html_link],
                                "doc_id": ["_".join([key,str(self.doc_date)])],
                                "doc_type": [doc_type],
                                "doc_date": [int(self.doc_date)],
                                "speaker": [speaker.lower()],
                                "speaker_text": [s],
                                "line_of_doc": [line_of_doc_cter]
                        }

                        self.save_corpus(html_link_dict)
                        print(line_of_doc_cter, s)

                        line_of_doc_cter+=1

            print("Done with %s - %s" %(key, html_link))

    def save_corpus(self, out_dict):
        '''
        Save dictionary to SQL database
        '''
        self.DB.save_to_db(self.table_name, out_dict)

    def fetch_data(self, htmlfile):
        '''Grabs and opens the html file given the url address'''
        url = htmlfile
        if url==None:
            print("No URL Provided")
        else:
            response = urllib.request.urlopen(url)

        return response.read()

    def clean_html(self, htmltext):
        '''Uses beautifulsoup to parse the html file and clean it a bit

           Returns two different arrays:
                speaker -- who was talking
                speaker_text -- that the speaker said.

           Useful, specificially for debates. Clean_text will provide, in
           chronological order, the speaker:what they said.
        '''
        soupy = BS(htmltext, 'lxml')

        # Get the document date. Save "March 16, 2015" as "20150316"
        date = str(soupy.find_all('span',class_='docdate'))
        date_str = " ".join(re.split(' |, ',re.sub(r"<.+?>|","", date)[1:-1]))
        stime = time.strptime(date_str,"%B %d %Y")
        self.doc_date = str((stime[0]*10000)+(stime[1]*100)+(stime[2]))

        text_only = str(soupy.find_all('span',class_='displaytext'))
        speaker = []
        speaker_text = []
        for each in text_only[1:-1].split('<p>'):
            clean_each = re.sub(r"<.+?>|\[.+?\]","", each)

            clean_each_split = clean_each.split(':')
            #print(clean_each_split)
            if len(clean_each_split) > 1:
                speaker.append(clean_each_split[0])
                try:
                    speaker_text.append(clean_each_split[1])
                except (AttributeError, TypeError):
                    pdb.set_trace()
            else:
                try:
                    speaker_text[-1] = speaker_text[-1]+' '+clean_each_split[0]
                except:
                    speaker_text.append(clean_each_split[0])

        return speaker, speaker_text

    def get_html_links(self):

        link_dict = {}

        link_dict['debate'] = [
                'http://www.presidency.ucsb.edu/ws/index.php?pid=115148',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=111711',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=111634',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=111500',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=111472',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=111412',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=111395',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=111177',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=110908',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=110906',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=110756',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=110489',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=111413',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=111394',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=111176',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=110909',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=110907',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=110758',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=110757',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=116995',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=112719',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=112718',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=111520',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=111471',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=111409',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=111178',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=110910',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=110903'
        ]

        link_dict['speech_trump'] = [
                'http://www.presidency.ucsb.edu/ws/index.php?pid=110306',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=116597'

        ]

        link_dict['speech_clinton'] = [
                'http://www.presidency.ucsb.edu/ws/index.php?pid=116600',
                'http://www.presidency.ucsb.edu/ws/index.php?pid=111596'
        ]

        self.html_links = link_dict

    #DEFUNCT
    def combine_speakers(self):
        speakers = self.speakers
        text = self.speakers_text
        uniq_speakers = list(set(speakers))

        speaker_dict = {}

        speakerarr = np.array(speakers)
        textarr = np.array(text)
        for us in uniq_speakers:
            match = np.where(speakerarr == us)[0]
            matched_text = textarr[match]

            giant_text_str = ''
            for mt in matched_text:
                re_mt = re.sub(r'\[.+?\]','', mt.tolist())
                giant_text_str+=re_mt

            speaker_dict[us] = giant_text_str

        self.speaker_dict = speaker_dict
