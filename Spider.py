import sqlite3
import urllib.error
import ssl
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Pages
    (id INTEGER PRIMARY KEY, url TEXT UNIQUE, html TEXT,
     error INTEGER, old_rank REAL, new_rank REAL)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Links
    (from_id INTEGER, to_id INTEGER)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Webs (url TEXT UNIQUE)''')

# Checking if data base is not already created
cur.execute('''Select id, url from Pages where html is null and error is null order by random() Limit 1''')
row = cur.fetchone()

if row is not None:
    print("ReStarting Crawl: or Delete spider.sqlite to start fresh crawl")
else:
    startUrl = input("Enter Url or Press Enter for default Url")
    if len(startUrl) < 1: startUrl = 'http://www.dr-chuck.com/'
    if startUrl.endswith('/'): startUrl = startUrl[:-1]

    web = startUrl

    """ Using  rfind() to get rid of html / htm files as we are concerned with links not html files """
    # https://www.geeksforgeeks.org/python-string-rfind/ Documentation of rfind()
    # https://python-data.dr-chuck.net/known_by_tamarah.html check using this example html page
    if startUrl.endswith('.html') or startUrl.endswith('.htm'):
        pos = startUrl.rfind('/')
        web = startUrl[:pos]
    print(web)
