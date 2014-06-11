import json
import urllib2

from webapp2 import uri_for
from datetime import datetime, timedelta, date

SEARCH_LIMIT = 3

#########
# PAGES #
#########
def get_page(url):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'}
    
    req = urllib2.Request(url, headers=hdr)
    resp = urllib2.urlopen(req)

    return resp


def get_revision_id(p, d):
    html = get_page('http://en.wikipedia.org/w/api.php?action=query&prop=revisions&format=json&titles=' + urllib2.quote(p) + '&rvprop=ids&rvstart=' + d)
    jsnr = json.load(html)['query']['pages']

    if jsnr.values()[0].has_key('revisions'):
        return jsnr.values()[0]['revisions'][0]['revid']

    else:
        return None


def fetch_wiki(p, d):
    # GET PAGE
    try:
        rev_id = long(p)
        
    except ValueError:
        rev_id = get_revision_id(p, d)

    html = get_page('http://en.wikipedia.org/w/index.php?oldid=' + str(rev_id)).read()

    # MODIFY MARKUP
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html)

    def _new_tilde_tag():
        tilde_tag = soup.new_tag('span')
        tilde_tag['style'] = 'color:rgba(6, 69, 173, 1);'
        tilde_tag.string = '~'

        return tilde_tag

    def _new_date_tag():
        date_tag = soup.new_tag('span', **{'class' : 'tilde'})
        date_tag.string = str(datetime.strftime(datetime.strptime(d, '%Y%m%d%H%M%S'), '%d %B, %Y'))

        return date_tag

    # REMOVE SUPERFLUOUS
    soup.find(id='contentSub').decompose()

    # APPEND HEADER
    heading = soup.find(id='firstHeading').span
    
    heading.append(_new_tilde_tag())
    heading.append(_new_date_tag())

    # REPLACE LINKS
    for link in soup.find('div', {'class':'mw-body-content'})('a'):

        if link['href'][0] == '#':
            pass

        elif link['href'][0:4] == 'Wiki':
            pass

        else:
            link.append(_new_tilde_tag())
            link['href'] = uri_for('Page', page=link['href'].split('/')[-1], timestamp=d)

    return soup


def search_wiki(q, d):
    # GET SEARCH RESULTS
    html = get_page('http://en.wikipedia.org/w/api.php?action=opensearch&limit=' + str(SEARCH_LIMIT) + '&search=' + urllib2.quote(q))
    jsnp = json.load(html)[1]

    # GET LATEST REVISIONS
    results = []

    for p in jsnp:
        rev_id = get_revision_id(p, d)

        if rev_id:
            results.append({
                'name'  : p, 
                'url'   : uri_for('Page', page=str(rev_id), timestamp=d)
            })

    return results



G_KEY = 'AIzaSyCjOYChDxIkvg0rPsu7PH3WZ103HRU7rFk'

G_CSE = '016459373861639011207:s6x5jgsujyo'

G_QRY = 'https://www.googleapis.com/customsearch/v1?' + \
            'key={key}&' + \
            'cx={cse}&' + \
            'q={qry}&' + \
            'alt=json&' + \
            'siteSearch=en.wikipedia.org'

            #'sort=date:r:{dts}:{dte}&' + \

def make_query(query, start=None, end=None):
    return G_QRY.format(
        key = G_KEY,
        cse = G_CSE,
        qry = query
    )