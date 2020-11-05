import sqlite3

conn = sqlite3.connect('spider.sqlite3')

cur = conn.cursor()

# Find the ids that send out page rank - we only are interested
# in pages in the SCC that have in and out links, While those pages which do not have in and out links are not
# considered

cur.execute('''Select Distinct from_id From Links''')
from_ids = list()
for row in cur:
    from_ids.append(row[0])

# Find the id that receive page rank
cur.execute('''Select Distinct from_id, to_id From Pages''')
to_ids = list()
links = list()
for row in cur:
    from_id = row[0]
    to_id = row[1]

    '''All these conditions imply a simple fact that one only accepts those pages which have inbound and outbound links 
    not any one of these either.'''
    if from_id == to_id: continue
    if from_id not in from_ids: continue
    if to_id not in from_ids: continue
    links.append(row)
    if to_id not in to_ids: to_ids.append(to_id)
