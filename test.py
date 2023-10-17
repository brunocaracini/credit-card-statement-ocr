from data.data import Data

d = Data()
d.openConn()

res = d.cursor.execute('Select * from credit_card_statements')
res = d.cursor.fetchall()
print(res)