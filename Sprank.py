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

# Collect latest Page ranks of strong Component/Links using Page rank Algorithm
prev_ranks = dict()
for node in from_ids:
    cur.execute('''Select new_rank from Pages where id = ?''',(node,))
    row = cur.fetchone()
    prev_ranks[node] = row[0]

sval = input('How many iterations: ')
many = 1
if (len(sval) > 0 ): many = int(sval)

# checking if prev_ranks dict got thing to rank or is empty
if len(prev_ranks) < 1:
    print('Nothing to Rank, Check Data/ Run Spider.py to crawl web Pages')
    quit()
