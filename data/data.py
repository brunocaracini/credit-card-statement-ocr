import MySQLdb

DATABASENAME = '`sql10462127`'

class Data():

    def __init__(self):
        cursor = None
        db = None

    def openConn(self):
        #Opens DB Connection
        self.db = MySQLdb.connect(host="sql10.freesqldatabase.com",
                     user="sql10462127",
                     passwd="eUsSDTYqKa",
                     db="sql10462127",
                     charset='utf8')
        self.cursor = self.db.cursor()
    
    def closeConn(self):
        self.db.close()
