import json
import urllib
import urllib2
import logging

from webapp2 import uri_for
from datetime import datetime, timedelta, date


#################
# PAGE : GOOGLE #
#################
# G_KEY = 'AIzaSyCjOYChDxIkvg0rPsu7PH3WZ103HRU7rFk'

# G_CSE = '016459373861639011207:s6x5jgsujyo'

# G_QRY = 'https://www.googleapis.com/customsearch/v1?alt=json' + \
#                                               '&key={key}' + \
#                                               '&cx={cse}' + \
#                                               '&q={qry}' + \
#                                               '&siteSearch=en.wikipedia.org'
#                                               #'&sort=date:r:{dts}:{dte}' + \

# def make_query(query, start=None, end=None):
#     return G_QRY.format(
#         key = G_KEY,
#         cse = G_CSE,
#         qry = query
#     )


###########
# GENERIC #
###########

def verbose_date(timestamp):
    return str(datetime.strftime(datetime.strptime(timestamp, '%Y%m%d%H%M%S'), '%d %B %Y'))


def get_response(url, kwargs={}):
    hdr = {'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'}

    url = url.format(**kwargs)

    logging.debug('REQUESTED: ' + url)

    rqst = urllib2.Request(url, headers=hdr)
    resp = urllib2.urlopen(rqst)

    return resp


###############
# PAGE : WIKI #
###############

WIKI_BASE = 'http://en.wikipedia.org'

WIKI_SEARCH_LIMIT = '5'

WIKI_URL_SEARCH =       WIKI_BASE + '/w/api.php?action=opensearch' + \
                                              '&limit=' + WIKI_SEARCH_LIMIT + \
                                              '&search={query}'

WIKI_URL_HISTORY =      WIKI_BASE + '/w/api.php?action=query' + \
                                              '&continue=' + \
                                              '&prop=revisions' + \
                                              '&format=json' + \
                                              '&rvprop=ids' + \
                                              '&titles={page_id}' + \
                                              '&rvstart={timestamp}'

WIKI_URL_PAGE_VERS =    WIKI_BASE + '/w/index.php?oldid={rev_id}'

WIKI_URL_PAGE_DFLT =    WIKI_BASE + '/wiki/{page_id}'


def get_revision_id(page_id, timestamp):
    html = get_response(WIKI_URL_HISTORY, {
            'page_id'   : urllib.quote_plus(page_id),
            'timestamp' : timestamp
        })

    jsnr = json.load(html)

    jsnp = jsnr['query']['pages'].values()[0]

    if jsnp.has_key('revisions'):
        rev_id = jsnp['revisions'][0]['revid']

    else:
        rev_id = None

    return rev_id


def search_wiki(query, timestamp):
    # GET SEARCH RESULTS
    html = get_response(WIKI_URL_SEARCH, {
            'query'     : urllib.quote_plus(query)
        })

    jsnp = json.load(html)

    # GET LATEST REVISIONS
    results = []

    for page_id in jsnp[1]:
        try:
            rev_id = get_revision_id(page_id, timestamp)

            if rev_id:
                results.append({
                    'name'  : page_id, 
                    'url'   : uri_for('Page', page_id=page_id, timestamp=timestamp)
                })

        except Exception:
            pass

    return results


def fetch_wiki(page_id, timestamp=None):

    # def _new_tilde_tag():
    #     tilde_tag = soup.new_tag('span', **{'class' : 'wiki-tilde-tilde !important'})
    #     tilde_tag.string = '~'

    #     return tilde_tag

    # def _new_date_tag():
    #     date_tag = soup.new_tag('span', **{'class' : 'wiki-tilde-date !important'})
    #     date_tag.string = verbose_date(timestamp)

    #     return date_tag


    # GET REVISION
    no_page = False

    if timestamp:
        rev_id = get_revision_id(page_id, timestamp)

        if not rev_id:
            no_page = True

        # GET PAGE
        html = get_response(WIKI_URL_PAGE_VERS, {
                'rev_id'    : rev_id
            })

    else:
        try:
            html = get_response(WIKI_URL_PAGE_DFLT, {
                'page_id'   : urllib.quote_plus(page_id)
            })

        except urllib.HTTPError, e:
            no_page = True

    if no_page:
        html = 'No wiki content existed for <b>' + page_id + '</b>'

        if timestamp:
            return html + ' at time <b>' + verbose_date(timestamp) + '</b>.'

        else:
            return html +'.'



    # MODIFY MARKUP
    from bs4 import BeautifulSoup

    html = html.read()
    soup = BeautifulSoup(html)

    # REMOVE SUPERFLUOUS
    soup.find(id='mw-head').decompose()
    soup.find(id='mw-page-base').decompose()
    soup.find(id='mw-navigation').decompose()

    soup.find(id='siteSub').decompose()
    soup.find(id='contentSub').decompose()
    soup.find(id='firstHeading').decompose()


    # APPEND HEADER
    # heading = soup.find(id='firstHeading')
    
    # heading.append(_new_tilde_tag())
    # heading.append(_new_date_tag())

    # REPLACE LINKS

    soup.find(id='content')['style'] = 'margin-left: 0 !important'

    for link in soup.find(id='bodyContent')('a'):
        link['class'] = link.get('class', []) + ['wiki-tilde']

        if link.has_key('rel'):
            pass

        elif '#' == link['href'][0]:
            pass

        elif ':' in link['href']:
            pass

        else:
            if link['href'][-11:] == 'redirect=no':
                new_page_id = link['href'].split('=')[1].split('&')[0]
                
            else:
                new_page_id = link['href'].split('/')[-1]


            if timestamp:
                link['href'] = uri_for('Page', page_id=new_page_id, timestamp=timestamp)

                tilde_tag = soup.new_tag('span', **{'class' : 'wiki-tilde-tilde'})
                tilde_tag.string = '~'

                link.append(tilde_tag)

            else:
                link['href'] = uri_for('PageDefault', page_id=new_page_id)

    return soup