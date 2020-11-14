import sqlite3

conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()

cur.execute('''Select Count(from_id) as inbound, old_rank, new_rank, url, id From Pages JOIN 
            Links on Pages.id = Links.to_id 
            Where html is not Null 
            group by id order by inbound DESC ''')

count = 0
for row in cur:
    if count < 50 : print(row)
    count = count + 1

print(count, "rows.")
conn.close()