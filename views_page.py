import json
import urllib
import urllib2
import logging
import views

from webapp2 import uri_for
from datetime import datetime, timedelta, date

import tools


USE_GOOGLE_SEARCH   = False

#################
# PAGE : GOOGLE #
#################

GOOGLE_BASE         = 'https://www.googleapis.com'

GOOGLE_SEARCH_LIMIT = '5'

GOOGLE_KEY          = 'AIzaSyCjOYChDxIkvg0rPsu7PH3WZ103HRU7rFk'

GOOGLE_CSE          = '016459373861639011207:s6x5jgsujyo'

GOOGLE_URL_SEARCH   = GOOGLE_BASE + '/customsearch/v1' + \
                                        '?alt=json' + \
                                        '&num=' + GOOGLE_SEARCH_LIMIT + \
                                        '&key=' + GOOGLE_KEY + \
                                        '&cx=' + GOOGLE_CSE + \
                                        '&q={terms}' + \
                                        '&siteSearch={site}' + \
                                        '&sort=date:r:{end}:{end}'


###############
# PAGE : WIKI #
###############

WIKI_BASE           = 'http://en.wikipedia.org'

WIKI_SEARCH_LIMIT   = '5'

WIKI_URL_SEARCH     = WIKI_BASE + '/w/api.php' + \
                                        '?action=opensearch' + \
                                        '&limit=' + WIKI_SEARCH_LIMIT + \
                                        '&redirects=resolve' + \
                                        '&search={terms}'

WIKI_URL_HISTORY    = WIKI_BASE + '/w/api.php' +\
                                        '?action=query' + \
                                        '&continue=' + \
                                        '&prop=revisions' + \
                                        '&format=json' + \
                                        '&rvprop=ids' + \
                                        '&titles={page_title}' + \
                                        '&rvstart={timestamp}'

WIKI_URL_PAGE_REV   = WIKI_BASE + '/w/index.php' + \
                                        '?oldid={rev_id}'

WIKI_URL_PAGE_NRM   = WIKI_BASE + '/wiki/{page_id}'


###########
# GENERIC #
###########

def get_response(url, context):
    hdr = {'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'}

    url = url.format(**context)

    logging.debug('REQUESTED: ' + url)

    rqst = urllib2.Request(url, headers=hdr)
    html = urllib2.urlopen(rqst)

    return html


###########
# ENTRIES #
###########

def search(terms, **kwargs):
    results = []

    # Find Results
    pages = []

    if USE_GOOGLE_SEARCH:
        html = get_response(GOOGLE_URL_SEARCH, {
                'terms' : urllib.quote(terms),
                'site'  : WIKI_BASE,
                'end'   : kwargs.get('timestamp', '')
            })

        jsnp = json.load(html)

        if jsnp.get('items'):
            pages = map(lambda p: ('-'.join(p['title'].split('-')[:-1]), p['link'].split('/')[-1:][0]), jsnp['items'])

    else:
        html = get_response(WIKI_URL_SEARCH, {
                'terms' : urllib.quote(terms)
            })

        jsnp = json.load(html)

        pages = zip(jsnp[1], map(lambda p: p.split('/')[-1:][0], jsnp[3]))


    # Check Result Existence
    for (page_title, page_id) in pages:
        result = {
            'page_id'       : page_id,
            'page_title'    : page_title,
            'is_match'      : urllib.unquote(terms) in [page_id, page_title]
        }

        if kwargs.get('timestamp'):
            timestamp = kwargs.get('timestamp')

            rev_id = None

            try:
                html = get_response(WIKI_URL_HISTORY, {
                        'page_title'    : urllib.quote(page_title),
                        'timestamp'     : timestamp.ljust(14, '0')
                    })

                jsnr = json.load(html)
                jsnp = jsnr['query']['pages'].values()[0]

                rev_id = None

                if jsnp.has_key('revisions'):
                    rev_id = jsnp['revisions'][0]['revid']

            except Exception as e:
                logging.error('views_page.search : error = ' + str(e))

            result.update({
                'is_invalid'    : not rev_id,
                'rev_id'        : rev_id,
                'timestamp'     : timestamp,
                'date'          : tools.to_verbose(t=timestamp)
            })

        if result['is_match'] and not result['is_invalid']:
            return [result]

        else:
            results.append(result)

    return results


def render(timestamp=None, rev_id=None, page_id=None, **kwargs):
    if kwargs.get('is_invalid'):
        return tools.render_to_string('page_non_existent.html', kwargs)

    else:
        if rev_id:
            logging.debug('views_page.render : revision')

            html = get_response(WIKI_URL_PAGE_REV, {
                    'rev_id'    : rev_id
                })

        else:
            logging.debug('views_page.render : default')

            html = get_response(WIKI_URL_PAGE_NRM, {
                    'page_id'   : page_id
                })
        
        # MODIFY MARKUP
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html)

        # REMOVE SUPERFLUOUS
        soup.find(id='mw-head').decompose()
        soup.find(id='mw-page-base').decompose()
        soup.find(id='mw-navigation').decompose()

        soup.find(id='siteSub').decompose()
        soup.find(id='contentSub').decompose()
        soup.find(id='firstHeading').decompose()
        soup.find(id='footer').decompose()

        soup.find(id='content')['style'] = 'margin-left: 0 !important'

        # UPDATE LINKS
        for link in soup.find(id='bodyContent')('a'):
            if link.has_key('rel'):
                pass

            elif '#' == link['href'][0]:
                pass

            elif ':' in link['href'] and not ':_' in link['href']:
                pass

            else:
                t = soup.new_tag('span', **{'class' : 'tilde-link'})

                t.string = ('~' if timestamp else '') + link.text
                t['terms'] = link['href'].split('/')[-1]
                t['termsv'] = link.text

                link.replaceWith(t)

        return str(soup.find(id='content'))