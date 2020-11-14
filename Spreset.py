import sqlite3

conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()
cur.execute('''Update Pages Set new_rank = 1.0 and old_rank = 0.0''')
conn.commit()

conn.close()

print('All pages set to rank 1.0')