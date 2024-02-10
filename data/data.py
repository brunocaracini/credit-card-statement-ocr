import pyodbc
from collections import namedtuple

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
        self.conn = None

    def openConn(self):
        # Opens DB Connection
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "Server=tcp:database.windows.net,1433;"
            "Database=ai-finance;"
            "Uid=bruno98980;"
            "Pwd=Br1to+98;"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )

        self.conn = pyodbc.connect("Driver={ODBC Driver 18 for SQL Server};Server=tcp:ai-finance.database.windows.net,1433;Database=ai-finance;Uid=bruno98980;Pwd=Br1to+98;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
        self.cursor = NamedTupleCursor(self.conn.cursor())
    
    def closeConn(self):
        self.conn.close()

    def insert(self, table, columns, values):
        self.openConn()
        insert_many = isinstance(values, list) and all(isinstance(elem, list) for elem in values)
        if not insert_many:
            values = [values]
        inserted_ids = []
        for val in values:
            query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['?']*len(val))})"
            self.cursor.execute(query, val)
            self.conn.commit()
            inserted_ids.append(self.cursor.execute("SELECT @@IDENTITY").fetchone()[0])
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
        query = f"UPDATE {table} SET {', '.join([f'{col}=?' for col in set_values.keys()])} WHERE {condition}"
        self.cursor.execute(query, list(set_values.values()))
        self.conn.commit()
        self.closeConn()

    def delete(self, table, condition):
        self.openConn()
        query = f"DELETE FROM {table} WHERE {condition}"
        self.cursor.execute(query)
        self.conn.commit()
        self.closeConn()
