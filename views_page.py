import json
import urllib
import urllib2
import logging
import views

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

def get_response(url, context):
    hdr = {'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'}

    url = url.format(**context)

    logging.debug('REQUESTED: ' + url)

    rqst = urllib2.Request(url, headers=hdr)
    html = urllib2.urlopen(rqst)

    return html


###############
# PAGE : WIKI #
###############

WIKI_BASE = 'http://en.wikipedia.org'

WIKI_SEARCH_LIMIT = '10'

WIKI_URL_SEARCH =       WIKI_BASE + '/w/api.php?action=opensearch' + \
                                              '&limit=' + WIKI_SEARCH_LIMIT + \
                                              '&redirects=resolve' + \
                                              '&search={terms}'

WIKI_URL_HISTORY =      WIKI_BASE + '/w/api.php?action=query' + \
                                              '&continue=' + \
                                              '&prop=revisions' + \
                                              '&format=json' + \
                                              '&rvprop=ids' + \
                                              '&titles={page_title}' + \
                                              '&rvstart={timestamp}'

WIKI_URL_PAGE_VERS =    WIKI_BASE + '/w/index.php?oldid={rev_id}'

WIKI_URL_PAGE_DFLT =    WIKI_BASE + '/wiki/{page_id}'


def search(terms, timestamp=None):
    results = []

    html = get_response(WIKI_URL_SEARCH, {
            'terms' : urllib.quote(terms)
        })

    jsnp = json.load(html)

    pages = zip(jsnp[1], map(lambda p: p.split('/')[-1:][0], jsnp[3]))

    for (page_title, page_id) in pages:
        result = {
            'title'     : page_title,
            'url'       : uri_for('Page', terms=page_id, tilds=timestamp or ''),
            'page_id'   : page_id
        }

        if timestamp:
            rev_id = None

            try:
                html = get_response(WIKI_URL_HISTORY, {
                        'page_title'    : urllib.quote(page_title),
                        'timestamp'     : timestamp
                    })

                jsnr = json.load(html)
                jsnp = jsnr['query']['pages'].values()[0]

                rev_id = None

                if jsnp.has_key('revisions'):
                    rev_id = jsnp['revisions'][0]['revid']

            except Exception as e:
                logging.error('views_page.search : error = ' + str(e))

            result.update({
                'is_match'      : page_id == terms and rev_id,
                'is_invalid'    : not rev_id,
                'rev_id'        : rev_id,
                'timestamp'     : timestamp,
                'date'          : datetime.strptime(timestamp, '%Y%m%d%H%M%S')
            })

        else:
            result.update({
                'is_match'  : page_id == terms
            })

        if result['is_match']:
            return [result]

        else:
            results.append(result)

    return results


def render(timestamp=None, rev_id=None, page_id=None, **kwargs):
    if kwargs.get('is_invalid'):
        return views.render_to_string('templates/page_non_existent.html', kwargs)

    else:
        if rev_id:
            logging.debug('views_page.render : revision')

            html = get_response(WIKI_URL_PAGE_VERS, {
                    'rev_id'    : rev_id
                })

        else:
            logging.debug('views_page.render : default')

            html = get_response(WIKI_URL_PAGE_DFLT, {
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
            link['class'] = link.get('class', []) + ['wiki-tilde']

            if link.has_key('rel'):
                pass

            elif '#' == link['href'][0]:
                pass

            elif ':' in link['href']:
                pass

            else:
                new_page_id = link['href'].split('/')[-1]

                # link['href'] = uri_for('Page', terms=new_page_id, tilds=timestamp or '')

                # if timestamp:
                #     tilde_tag = soup.new_tag('span', **{'class' : 'wiki-tilde-tilde'})
                #     tilde_tag.string = '~'

                #     link.append(tilde_tag)


                new_link = soup.new_tag('span', **{'class' : 'link'})
                try:
                    new_link.string = ('~' if timestamp else '') + str(link.string)
                except Exception:
                    new_link.string = 'Error'
                new_link['terms'] = new_page_id
                new_link['tilds'] = timestamp or ''

                link.replaceWith(new_link)

        return str(soup.find(id='bodyContent'))