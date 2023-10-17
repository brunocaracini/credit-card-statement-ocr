import MySQLdb
from collections import namedtuple

DATABASENAME = '`sql10462127`'

class NamedTupleCursor:
    def __init__(self, cursor):
        self._cursor = cursor
    
    def __getattr__(self, item):
        return getattr(self._cursor, item)
    
    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        else:
            return namedtuple('Result', [d[0] for d in self._cursor.description])(*row)
        
    def fetchall(self):
        rows = self._cursor.fetchall()
        return [namedtuple('Result', [d[0] for d in self._cursor.description])(*row) for row in rows]

class Data():

    def __init__(self):
        self.cursor = None
        self.db = None

    def openConn(self):
        # Opens DB Connection
        self.db = MySQLdb.connect(
            host="localhost",
            user="root",
            passwd="3936107",
            db="aifinance",
            charset='utf8'
        )
        self.cursor = NamedTupleCursor(self.db.cursor())
    
    def closeConn(self):
        self.db.close()

    def insert(self, table, columns, values):
        self.openConn()
        insert_many = True if (isinstance(values, list) and all(isinstance(elem, list) for elem in values)) else False
        if not insert_many:
            values = [values]
        inserted_ids = []
        for val in values:
            query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['%s']*len(val))})"
            self.cursor.execute(query, val)
            inserted_ids.append(self.cursor.lastrowid)
        self.db.commit()
        self.closeConn()
        return inserted_ids if insert_many else inserted_ids[0]

    def select(self, table, columns=None, condition=None):
        self.openConn()
        if columns:
            columns = ', '.join(columns)
        else:
            columns = '*'
        query = f"SELECT {columns} FROM {table}"
        if condition:
            query += f" WHERE {condition}"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.closeConn()
        return result

    def update(self, table, set_values, condition):
        self.openConn()
        query = f"UPDATE {table} SET {', '.join([f'{col}=%s' for col in set_values.keys()])} WHERE {condition}"
        self.cursor.execute(query, list(set_values.values()))
        self.db.commit()
        self.closeConn()

    def delete(self, table, condition):
        self.openConn()
        query = f"DELETE FROM {table} WHERE {condition}"
        self.cursor.execute(query)
        self.db.commit()
        self.closeConn()
