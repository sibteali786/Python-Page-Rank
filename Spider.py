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
    startUrl = input("Enter Url or Press Enter for default Url: ")
    if len(startUrl) < 1: startUrl = 'http://www.dr-chuck.com/'
    if startUrl.endswith('/'): startUrl = startUrl[:-1]

    web = startUrl

    """ Using  rfind() to get rid of html / htm files as we are concerned with links not html files """
    # https://www.geeksforgeeks.org/python-string-rfind/ Documentation of rfind()
    # https://python-data.dr-chuck.net/known_by_tamarah.html check using this example html page
    if startUrl.endswith('.html') or startUrl.endswith('.htm'):
        pos = startUrl.rfind('/')
        web = startUrl[:pos]

    #print(web)

    if ( len(startUrl) > 1):
        cur.execute('''Insert or ignore into Webs (url) values (?)  ''', (web,))
        cur.execute('''Insert or ignore into Pages (url, html, new_rank) values (?, Null,1.0 )''',(startUrl,))
        conn.commit()

cur.execute('''select url from Webs''')
webs = list()
for row in cur:
   webs.append(str(row[0]))

print(webs)

# How many pages to get for a current given Web
many = 0

while True:

    if ( many < 1 ):
        sVal = input("How many Pages to get: ")

        if (len(sVal) < 1): break
        many = int(sVal)

    many = many - 1
    cur.execute('''select id, url from Pages where html is null and error is null ORDER BY Random() LIMIT 1''')
    try:
        row = cur.fetchone()
        # print row
        fromid = row[0]
        url = row[1]
    except:
        print('No unretrieved HTML pages found')
        many = 0
        break

    print(fromid, url, end=' ')

    try:
        '''https://www.geeksforgeeks.org/python-urllib-module/
        Check Documentation for urllib module'''
        document = urlopen(url, context= ctx)
        html = document.read()
        # https://stackoverflow.com/questions/1726402/in-python-how-do-i-use-urllib-to-see-if-a-website-is-404-or-200
        '''
            The getcode() method (Added in python2.6) returns the HTTP status code that was sent with the response, or None if the URL is no HTTP URL.

            >>> a=urllib.urlopen('http://www.google.com/asdfsf')
            >>> a.getcode()
            404
            >>> a=urllib.urlopen('http://www.google.com/')
            >>> a.getcode()
            200
            '''
        if document.getcode() != 200:
            print("Error on Page: ",document.getcode())
            cur.execute('UPDATE Pages SET error=? WHERE url=?', (document.getcode(), url))
        '''https://stackoverflow.com/questions/12474406/python-how-to-get-the-content-type-of-an-url/36882727
        use for learning how info.get_content_type() works'''
        if 'text/html' != document.info().get_content_type():
            print("Ignore non text/html page")
            cur.execute('''Delete from Pages where url = ?''', (url,))
            conn.commit()
            continue
        print('('+"Size of html page received: ", str(len(html)) + ')')

        soup = BeautifulSoup(html, 'html.parser')
        '''https://www.geeksforgeeks.org/implementing-web-scraping-python-beautiful-soup/
        Documentation and working of Beautiful Soup'''

    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        break
    except Exception as e:
        print(str(e))
        print("Unable to retrieve or parse page")
        cur.execute('UPDATE Pages SET error=-1 WHERE url=?', (url,))
        conn.commit()
        continue
    print(url)
    cur.execute('''Insert or ignore into Pages (url, html , new_rank) Values (?, NULL, 1.0)''',(url,))
    cur.execute('''Update Pages Set html = ? where url = ?''',(memoryview(html), url))
    conn.commit()

    # Retreiving All anchor tags
    tags = soup('a')
    count = 0
    for tag in tags:
        '''https://www.geeksforgeeks.org/get-method-dictionaries-python/
        For understanding working of get() method '''
        href = tag.get('href', None)
        '''https://www.w3schools.com/tags/att_a_href.asp
        href documentation in html'''
        if (href is None ): continue
        # Resolve relative references like href="/contact" so as to only pick actual absolute url
        splitted_url = urlparse(href)

        '''https://stackoverflow.com/questions/21687408/how-to-remove-scheme-from-url-in-python
        For dealing with schemes of the url'''
        # Since if an url has no scheme like https/http then we would go to https page if we click on it which is good
        # we are still in need of an absolute url as here we might not be on same page when we are retrieving that page.
        if (len(splitted_url.scheme) < 1):
            href = urljoin(url, href)
        ''' href has Link to an element with a specified id within the page (like href="#section2")'''
        element_in_page = href.find('#')
        if (element_in_page > 1): href = href[:element_in_page]
        # For dealing with links to images/videos and any other things
        if( href.endswith('.png') or href.endswith('.jpg') or href.endswith('.gif') ): continue
        if (href.endswith('/')): href = href[:-1]

        print(href)

        if (len(href) < 1): continue

        # Checking if current url is already in the retrieved web urls or not
        found = False
        for web in webs:
            if (href.startswith(web)):
                found = True
                break
        if not found: continue
        cur.execute('''Insert or ignore into Pages (url, html, new_rank) Values (? , Null, 1.0)''',(href,))
        count += 1
        conn.commit()

        cur.execute('SELECT id FROM Pages WHERE url=? LIMIT 1', (href,))
        try:
            row = cur.fetchone()
            toid = row[0]
        except:
            print('Could not retrieve id')
            continue
        # print fromid, toid
        cur.execute('INSERT OR IGNORE INTO Links (from_id, to_id) VALUES ( ?, ? )', (fromid, toid))

    print(count)

cur.close()






