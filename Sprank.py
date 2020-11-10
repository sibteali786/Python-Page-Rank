import sqlite3

conn = sqlite3.connect('spider.sqlite')

cur = conn.cursor()

# Find the ids that send out page rank - we only are interested
# in pages in the SCC that have in and out links, While those pages which do not have in and out links are not
# considered

cur.execute('''Select Distinct from_id From Links''')
from_ids = list()
for row in cur:
    from_ids.append(row[0])

# Find the id that receive page rank
cur.execute('''Select Distinct from_id, to_id From Links''')
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
    cur.execute('''Select new_rank from Pages where id = ?''', (node,))
    row = cur.fetchone()
    prev_ranks[node] = row[0]

sval = input('How many iterations: ')
many = 1
if (len(sval) > 0): many = int(sval)

# checking if prev_ranks dict got thing to rank or is empty
if len(prev_ranks) < 1:
    print('Nothing to Rank, Check Data/ Run Spider.py to crawl web Pages')
    quit()

# ranking a page in Memory helps us fast the process to retreive and use a data with copying actual data
""" Applying Page rank Algorithm """
for i in range(many):
    # print prev_ranks.items()[:5]
    next_ranks = dict();
    total = 0.0
    for (node, old_rank) in list(prev_ranks.items()):
        total = total + old_rank
        next_ranks[node] = 0.0
    # print total

    # Find the number of outbound links and sent the page rank down each
    for (node, old_rank) in list(prev_ranks.items()):
        # print node, old_rank
        give_ids = list()
        for (from_id, to_id) in links:
            if from_id != node: continue
            #  print '   ',from_id,to_id

            if to_id not in to_ids: continue
            give_ids.append(to_id)
        if (len(give_ids) < 1): continue
        amount = old_rank / len(give_ids)
        # print node, old_rank,amount, give_ids

        for id in give_ids:
            next_ranks[id] = next_ranks[id] + amount

    newtot = 0
    for (node, next_rank) in list(next_ranks.items()):
        newtot = newtot + next_rank
    evap = (total - newtot) / len(next_ranks)

    # print newtot, evap
    for node in next_ranks:
        next_ranks[node] = next_ranks[node] + evap

    newtot = 0
    for (node, next_rank) in list(next_ranks.items()):
        newtot = newtot + next_rank

    totdiff = 0
    for (node, old_rank) in list(prev_ranks.items()):
        new_rank = next_ranks[node]
        diff = abs(old_rank - new_rank)
        totdiff = totdiff + diff

    avediff = totdiff / len(prev_ranks)
    print(i + 1, avediff)

    # rotate
    prev_ranks = next_ranks

# Put the final ranks back into the database
print(list(next_ranks.items())[:5])
cur.execute('''UPDATE Pages SET old_rank=new_rank''')
for (id, new_rank) in list(next_ranks.items()):
    cur.execute('''UPDATE Pages SET new_rank=? WHERE id=?''', (new_rank, id))
conn.commit()
cur.close()