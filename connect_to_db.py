from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd
import pdb

#sql_query = """
#SELECT * FROM birth_data_table WHERE delivery_method='Cesarean';
#"""

class ConnectToDB(object):
    def __init__(self):
        dbname = 'polibot_db'
        username = 'dpmorg_mac'
        pswd = 'OpaOpa'

        self.engine = create_engine('postgresql://%s:%s@localhost/%s'
                %(username,pswd,dbname))

        if not database_exists(self.engine.url):
            create_database(self.engine.url)

        self.con = None
        self.con = psycopg2.connect(database=dbname,
                                    user=username,
                                    host='localhost',
                                    password=pswd)

    def save_to_db(self, table_name, input_dict):

        temp_df = pd.DataFrame.from_dict(input_dict)

        if table_name=="corpus_table":
            entry_id = "corpus_id"
        elif table_name=="question_table":
            entry_id = "question_id"
        elif table_name=="response_table":
            entry_id = "response_id"
        elif table_name=="tokens_table":
            entry_id = "token_id"

        unique_entry = input_dict[entry_id][0]

        #test_entry = self.check_entry_exists(table_name, entry_id, unique_entry)
        #if test_entry:
        #    pdb.set_trace()
        #    temp_df.to_sql(table_name, self.engine, if_exists='replace')
        #else:
        temp_df.to_sql(table_name, self.engine, if_exists='append')

    def pull_from_db(self, sql_query):
        data_request = pd.read_sql_query(sql_query, self.con)
        return data_request

    def pull_candidate_corpus(self, table_name, candidate):

        sql_query = """
        SELECT speaker, speaker_text
        FROM %s
        WHERE speaker='%s'
        ORDER BY doc_date DESC, line_of_doc ASC;
        """ %(table_name, candidate)

        candidate_pd = self.pull_from_db(sql_query)
        sent = [s for s in candidate_pd['speaker_text']]
        return " ".join(sent)

    def check_entry_exists(self, table_name, entry_id, entry):

        cursor = self.con.cursor()
        data = cursor.execute("SELECT count(*) FROM %s WHERE %s=%s"
                %(table_name, entry_id, entry))
        data = cursor.fetchone()[0]
        if data==0:
            return False
        else:
            return True

    """
    def check_table_exists(self, table_name):
        '''
        Check if the table exists. Return True/False
        '''
        if self.engine.dialect.has_table(self.engine, table_name):
            return True
        else:
            return False

    def create_table(self, table_name):
        '''
        Create table
        '''
    """
