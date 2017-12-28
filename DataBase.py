##################################### DataBase #################################
''' serve python-mysqldb --> apt install python-mysqldb '''
import MySQLdb

from utils import *

class DataBase:
    
    def __init__(self, config):
        try:
            self.db_connection = MySQLdb.connect(host=config['db_host'],
                                 user=config['db_user'],
                                 passwd=config['db_passwd'],
                                 db=config['db_name'])
            print("[DATABASE] connesso")
        except:
            print("[DATABASE] non riesco a connettermi al database")
            quit()

        # creo il cursore per utilizzare il database
        self.db = self.db_connection.cursor()

    #eseguo la query e aggiorno il database
    #ritorno il risultato della query
    def execute(self, query):
        self.db.execute(query)
        self.db_connection.commit()
        return self.db.fetchall()

    #chiude la connessione con il database
    def close(self):
        self.db_connection.close()

