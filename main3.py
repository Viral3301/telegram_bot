import sqlite3
import datetime
con = sqlite3.connect("database.db")
cur = con.cursor()

tgid = 12312321


a = datetime.datetime.now()

# print(a)
client_activesql = cur.execute(f'Select is_active from tg_active where is_active={client_id[0][0]}')
client_active = client_activesql.fetchall()

print(client_active)


