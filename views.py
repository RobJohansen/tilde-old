from google.appengine.api import users, datastore_errors

from webapp2 import RequestHandler, uri_for

from datetime import datetime, timedelta, date



import jinja2
import os
import json

import logging

from operator import itemgetter


import models
import pages


#############
# RENDERERS #
#############
J_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


def json_response(self, context):
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(context))


def render_with_context(self, filename, context):
    context.update({})

    template = J_ENV.get_template('templates/' + filename)
    self.response.out.write(template.render(context))


#########
# VIEWS #
#########
class Home(RequestHandler):
    def get(self):
        context = {
            'tilds'     : self.request.get('ts')
        }

        render_with_context(self, 'home.html', context)


class Results(RequestHandler):
    def get(self, query, tilds):
        timestamp = models.get_timestamp(tilds)
        context = pages.search_wiki(query, timestamp)

        json_response(self, context)


class Tilds(RequestHandler):
    def get(self, tilds):
        context = models.get_next_tilds(tilds)

        json_response(self, context)


class Page(RequestHandler):
    def get(self, page, timestamp):
        t = pages.fetch_wiki(page, timestamp)

        self.response.out.write(t)


class Timeline(RequestHandler):
    def get(self, tilds):
        n = models.get_current_tild(tilds)

        # Populate
        results = []

        context = { }

        if n:
            results = [n] + list(n.children())

            if n.ancestor:
                results.append(n.ancestor.get())
                results.extend(n.ancestor.get().children())

            diff = (n.end - n.start) / 10

            def _to_json_date(d):
                return d.strftime("%Y-%m-%d")

            context.update({
                'min'       : _to_json_date(n.start - diff),
                'max'       : _to_json_date(n.end + diff),
                'custom'    : _to_json_date(n.end) #.seen_date('Lost'))
            })

        else:
            results = []

        results = zip(results, [True] + [False] * (len(results) - 1))
        results = sorted(map(lambda (x, b): x.to_calendar_node(b), results), key=itemgetter('start'))

        # Build
        from gviz_api import DataTable

        table = DataTable({
            'start'     : ('date', 'Start'),
            'end'       : ('date', 'End'),
            'content'   : ('string', 'Content'),
            'group'     : ('string', 'Group'),
            'className' : ('string', 'Class')
        })

        table.LoadData(results)


        context.update({
            'data'      : table.ToJSon(),
        })

        # Render
        json_response(self, context)


class Derive(RequestHandler):
    def get(self, id):
        context = {
            'tilds'     : models.derive_tilds(id)
        }

        json_response(self, context)


class SeenTag(RequestHandler):
    def post(self, id):
        m = models.Tilde.get_by_id(id) or models.Tilde.get_by_id(long(id))

        d = m.end

        while m.ancestor:
            m = m.ancestor.get()

        models.process_completion(m.key.id(), d)


class SeenTime(RequestHandler):
    def post(self, id, year, month, day):
        d = datetime(long(year), long(month), long(day))

        models.process_completion(id.split('~')[1], d)


class Test(RequestHandler):
    def get(self):
        self.response.write(models.seen_date('Lost'))












        # def _combinations(xs):
        #     from itertools import chain as xn, combinations as cmb
        #     return map(' '.join, xn(*map(lambda i: cmb(xs, i), range(1, len(xs) + 1))))








# class Home(RequestHandler):
#     def get(self):
#         context = {
#             'tilds'     : []
#         }

#         render_with_context(self, 'home.html', context)




# class DeriveTilds(RequestHandler):
#     def get(self):
#         k = self.request.get('key')
#         t = models.Tilde.get_by_id(k) or models.Tilde.get_by_id(long(k))

#         tilds = [t.verbose(tag=t.tag, key=str(t.key.id()))]
#         while t.ancestor:
#             t = t.ancestor.get()
#             tilds.append(t.verbose(tag=t.tag, key=str(t.key.id())))

#         context = {
#             'tilds'     : tilds
#         }

#         json_response(self, context)


# class Results2(RequestHandler):
#     def get(self):
        # q = self.request.get('qry')
        #k = self.request.get('key') # Change to be based on saved seen
        #t = models.Tilde.get_by_id(k) or models.Tilde.get_by_id(long(k))

        # context = { 'results' : [] }

        # result = {
        #             'text'  : "Hello",
        #             'id'    : 100,
        #             'url'   : 'http://en.wikipedia.org/w/index.php?title={p}&oldid={id}'.format(id=100, p='Hello')
        #         }

        # context['results'].append(result)

        # json_response(self, context)


        # t = models.Tilde.query().get()

        # url = make_query(q, t.start, t.end)
        # logging.info(url)
        # resp = urllib2.urlopen(url)
        # html = json.load(resp)['items']

        # context = { 'results' : [] }

        # for p in map(lambda d: d['formattedUrl'].split('/wiki/')[1], html):
        #     url = 'http://en.wikipedia.org/w/index.php?title={p}&action=history&year={year}&month={month}'.format(
        #         p = p,
        #         year = str(t.end.year),
        #         month = str(t.end.month)
        #     )

        #     from bs4 import BeautifulSoup

        #     hdr = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'}
        #     req = urllib2.Request(url, headers=hdr)
        #     soup = BeautifulSoup(urllib2.urlopen(req))

        #     import re
        #     section = soup.find(id=re.compile('mw-diff'))

        #     if section:
        #         i = section.get('value')

        #         result = {
        #             'text'  : p,
        #             'id'    : i,
        #             'url'   : 'http://en.wikipedia.org/w/index.php?title={p}&oldid={id}'.format(id=i, p=p)
        #         }

        #     context['results'].append(result)


        # json_response(self, context)





# def derive_tilde(terms):
#     ts = terms.split(' ')
#     cs = combs(xs)

#     roots = [n for n in [models.Tilde.get_by_id(c) for c in cs] if n]

#     if len(roots) > 1: # OPTIONS
#         return roots[0]

#     elif len(roots) == 1: # ROOT
#         return roots

#     else: # ALL TIME
#         return None
        

#     # leaves = []

#     # ys = map(models.Tilde.get_by_id, xs)

#     # if any(ys):

#     # else:


#     # # try:
#     # #     x = xs[next(i for i, j in enumerate(ys) if j)]

#     # for w in terms.split(' '):
#     #     n = models.Tilde.get_by_id(w) or leaves.append(m)

#     #     # Multiple should be a 'did you mean' list
#     #     # but only if more than one has tags matching the label

#     # ms = [n]

#     # for tag in n.label.tag:
#     #     if len(ms) > 0:
#     #         for m in ms:
#     #             if tag.format(tag = m.tag, key = n.key().id_or_name()) in cs:
#     #                 n = m
#     #                 break

#     #         ms = sum([list(m.children) for m in ms], [])

#     return n




        #dts = start.strftime('%Y%m%d'),
        #dte = end.strftime('%Y%m%d'),







# class Test(RequestHandler):
#     def get(self):
#         render_with_context(self, 'results.html', context)

# class DoStuff(RequestHandler):
#     def get(self):
#         pass
#         # x = models.Typde(key_name='Show')
#         # x.tag = ['{key}', 'Season {tag}', 'Episode {tag}']
#         # x.put()

#         # y = models.Tilde(key_name='Lost')
#         # y.label = models.Typde.get_by_key_name('Show')
#         # y.start = datetime(2004,9,22)
#         # y.end = datetime(2010,5,23)
#         # y.put()





# class Test(RequestHandler):
#     def get(self, t=None):
#         if t:
#             m = models.Tilde.get_by_id(t) or models.Tilde.get_by_id(long(t))

#             tilds = map(lambda x: { 'text': x.tag, 'value' : x.key.id() }, m.children)

#         else:
#             tilds = [{'text': 'Lost', 'value' : 'Lost'}]


#         context = {
#             't'     : t,
#             'data'  : { 'tilds' : tilds }
#         }

#         render_with_context(self, 'test.html', context)

#     def post(self):
#         q = self.request.get('q')
#         t = self.request.get('tilds')

#         Test.get(self, t)

