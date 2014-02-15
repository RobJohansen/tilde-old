from google.appengine.ext import db
from google.appengine.api import users, datastore_errors

from datetime import datetime, timedelta, date
from calendar import Calendar, monthrange
from webapp2 import RequestHandler, uri_for

import urllib
import models

import jinja2
import os

import urllib2
import json as j


import logging

from itertools import chain as xn, combinations as cmb
from operator import itemgetter




G_KEY = 'AIzaSyCjOYChDxIkvg0rPsu7PH3WZ103HRU7rFk'

G_CSE = '016459373861639011207:s6x5jgsujyo'

G_QRY = 'https://www.googleapis.com/customsearch/v1?' + \
            'key={key}&' + \
            'cx={cse}&' + \
            'q={qry}&' + \
            'alt=json&' + \
            'siteSearch=en.wikipedia.org'

            #'sort=date:r:{dts}:{dte}&' + \

def make_query(s, e, q):
    return G_QRY.format(
        key = G_KEY,
        cse = G_CSE,
        dts = s.strftime('%Y%m%d'),
        dte = e.strftime('%Y%m%d'),
        qry = q
    )

J_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def render_with_context(self, filename, context):
    context.update({})

    template = J_ENV.get_template('templates/' + filename)
    self.response.out.write(template.render(context))



def combs(xs):
    return map(' '.join, chain(*map(lambda i: combinations(xs, i), range(1, len(xs) + 1))))


def derive_tilde(terms):
# Initialize Site object

    # ts = terms.split(' ')
    # cs = combs(xs)

    # # Find Root Node
    # rs = map(models.Tilde.get_by_key_name, cs)

    # leaves = []


    # ys = map(models.Tilde.get_by_key_name, xs)

    # if any(ys):

    # else:


    # try:
    #     x = xs[next(i for i, j in enumerate(ys) if j)]



    for w in terms.split(' '):
        n = models.Tilde.get_by_key_name(w) or leaves.append(m)

        # Multiple should be a 'did you mean' list
        # but only if more than one has tags matching the label




    ms = [n]

    for tag in n.label.tag:
        if len(ms) > 0:
            for m in ms:
                if tag.format(tag = m.tag, key = n.key().id_or_name()) in cs:
                    n = m
                    break

            ms = sum([list(m.children) for m in ms], [])

    return n







class Home(RequestHandler):
    def get(self):
        s = self.request.get('s')
        t = self.request.get('t')
        n = self.request.get('n')

        try:
            c = models.Tilde.get(n) or None

            import gviz_api

            table = gviz_api.DataTable({
                'start'     : ('date', 'Start'),
                'end'       : ('date', 'End'),
                'content'   : ('string', 'Content'),
                'group'     : ('string', 'Group'),
                'className' : ('string', 'Class')
            })
            ds = []

            for x in [c.ancestor, c] + list(c.children) + (list(c.ancestor.children) if c.ancestor else []):
                tild = {}

                if x == None:
                    tild['group'] = 'All Time'

                    url = '<a href="?s={s}">{text}</a>'.format(
                        s = s,
                        text = 'All Time'
                    )

                    tild.update({
                        'start'     : c.start - timedelta(days=100),
                        'end'       : c.end + timedelta(days=100),
                        'content'   : url
                    })

                else:
                    tild['group'] = x.verbose()

                    text = x.verbose(tag = x.tag, key = x.key().id_or_name())

                    if x == c:
                        tild['className'] = 'current'

                        url = text

                    else:
                        url = '<a href="?s={s}&t={t}&n={n}">{text}</a>'.format(
                            s = s,
                            t = text,
                            n = str(x.key()),
                            text = text
                        )

                    tild.update({
                        'start'     : x.start,
                        'content'   : url
                    })

                    if not x.end == x.start:
                        tild['end'] = x.end + timedelta(days=1)
                
                ds.append(tild)



            table.LoadData(sorted(ds, key=itemgetter('start')))
            ds = table.ToJSon()

        except datastore_errors.BadKeyError:
            uri = '{uri}?s={s}'.format(
                s = s,
                uri = self.request.uri.partition('?')[0]
            )

            self.redirect(str(uri))

        finally:
            context = {
                's'         : s,
                't'         : t,
                'n'         : c,
                'data'      : ds
            }

            render_with_context(self, 'home.html', context)
        

    def post(self):
        s = self.request.get('terms')
        t = self.request.get('tilds')

        logging.getLogger().setLevel(logging.DEBUG)

        n = derive_tilde(t)

        uri = '{uri}?s={s}&t={t}&n={n}'.format(
            uri = self.request.uri.partition('?')[0],
            n = str(n.key()),
            s = s,
            t = t
        )

        self.redirect(str(uri))



class Results(RequestHandler):
    def get(self):
        n = models.Tilde.get(self.request.get('n'))

        rs = []

        dat = urllib2.urlopen(make_query(n.start, n.end, self.request.get('s')))
        dat = j.load(dat)['items']
        dat = map(lambda d: d['formattedUrl'].split('/wiki/')[1], dat)

        for d in dat:
            url = 'http://en.wikipedia.org/w/index.php?title={text}&action=history&year={year}&month={month}'.format(
                text = d,
                year = str(n.end.year),
                month = str(n.end.month)
            )

            hdr = {'User-Agent': 'Mozilla/5.0'}
            req = urllib2.Request(url, headers=hdr)
            page = urllib2.urlopen(req)

            for line in page.readlines():
                if 'id="mw-diff-' in line:
                    rs.append({'text' : d, 'id' : line.split('id="mw-diff-')[1][:12].split('"')[0] })
                    break

        context = {
            'results'   : rs
        }

        # //     'min'     : {{ 'new Date(%s, 1, 1)'|format(n.start.year)|safe }},
        # //     'max'     : {{ 'new Date(%s, 1, 1)'|format(n.end.year + 1)|safe }},
        # //     'zoomMin' : 3600000 * 24,
        # //     'zoomMax' : 3600000 * 24 * 31 * 12 * 10
        # // };

        render_with_context(self, 'results.html', context)




class Test(RequestHandler):
    def get(self):
        

        render_with_context(self, 'results.html', context)



class DoStuff(RequestHandler):
    def get(self):
        x = models.Typde(key_name='Show')
        x.tag = ['{key}', 'Season {tag}', 'Episode {tag}']
        x.put()

        y = models.Tilde(key_name='Lost')
        y.label = models.Typde.get_by_key_name('Show')
        y.start = datetime(2004,9,22)
        y.end = datetime(2010,5,23)
        y.put()


# G_DATE = datetime.now()

# def init_global_date():
#     global G_DATE
#     G_DATE = datetime.now()


# def update_global_date(y, m=None, d=None):
#     global G_DATE
#     G_DATE = datetime(y, m if m else G_DATE.month, d if d else G_DATE.day)



# class Test(RequestHandler):
#     def get(self, y1, m1, d1, y2, m2, d2):
#         l = datetime(int(y1), int(m1), int(d1))
#         r = datetime(int(y2), int(m2), int(d2))


#         d = r - l

#         i = 0

#         if abs(r.time().seconds - l.time.seconds) > 10: i = 1
#         if abs(d.time.hours) > 12: i = 3
#         if abs(d.days) > 7: i = 4
#         if abs(d.weeks) > 4: i = 5
#         if abs(d.months) > 6: i = 6
#         if abs(d.years) > 0: i = 7


#         context = {
#             'min'       : l,
#             'max'       : r,
#             'd'         : str(d) + ['Day', 'Month', 'Year', 'Day', 'Month', 'Year', 'asd'][i]
#         }

#         render_with_context(self, 'home.html', context)


# class Agenda(RequestHandler):
#     def get(self):
#         events = models.get_events(
#                     date_min=datetime.now()
#                  )

#         def _link(caption, c, s, order):
#             return {
#                 'a'         : order,
#                 'caption'   : caption,
#                 'url'       : uri_for(s, year=c.year, month=c.month, day=c.day).partition('?')[0]
#             }

#         items = [ {
#             'year'      : _link(verbose_year(e.date), e.date, 'Year', e.date.year),
#             'month'     : _link(verbose_month(e.date), e.date, 'Month', e.date.month),
#             'day'       : _link(verbose_day(e.date), e.date, 'Day', e.date.day),
#             'time'      : verbose_time(e.date),
#             'event'     : e
#         } for e in events ]

#         context = {
#             'header'    : 'Agenda',
#             'items'     : items
#         }

#         render_with_context(self, 'calendar/agenda.html', context)


# class Year(RequestHandler):
#     def get(self, year):
#         y = int(year)

#         update_global_date(y)

#         def _info(m):
#             events = models.get_events(
#                         date_min=datetime(y, m, 1),
#                         date_max=datetime(y, m, 1)+timedelta(days=monthrange(y, m)[1])
#                      )

#             return {
#                 'caption'   : verbose_month(m, trim=True),
#                 'url'       : uri_for('Month', year=y, month=m),
#                 'info'      : aggregate_info(events,'{day} <b>{description}</b>')
#             }

#         def _header_link(change):
#             c = datetime(y + change, 1, 1)

#             return {
#                 'caption'   : verbose_year(c),
#                 'url'       : uri_for('Year', year=c.year)
#             }

#         context = {
#             'header'    : verbose_year(y),
#             'links'     : {
#                             'prev'  : _header_link(-1),
#                             'next'  : _header_link(+1)
#                           },
#             'items'     : partition(map(_info, range(1, 13)), 4)
#         }

#         render_with_context(self, 'calendar/layout/year.html', context)


# class Month(RequestHandler):
#     def get(self, year, month):
#         y = int(year)
#         m = int(month)

#         update_global_date(y, m)

#         def _info(c):
#             events = models.get_events(
#                         date_min=c,
#                         date_max=c+timedelta(days=1)
#                      )

#             def _class(c):
#                 if c.month == m:
#                     if c == datetime.now().date():
#                         return 'today'

#                     else:
#                         return 'inside'

#                 else:
#                     return 'outside'

#             return {
#                 'caption'   : verbose_day(c, trim=True),
#                 'url'       : uri_for('Day', year=c.year, month=c.month, day=c.day) if c.month == m else uri_for('Month', year=c.year, month=c.month),
#                 'info'      : aggregate_info(events, '{time} <b>{description}</b>'),
#                 'class'     : _class(c)
#             }

#         def _header_link(change):
#             if m + change == 13:
#                 dy = y+1

#             elif m + change == 0:
#                 dy = y-1

#             else:
#                 dy = y

#             c = datetime(dy, (m + change - 1) % 12 + 1, 1)

#             return {
#                 'caption'   : verbose_month(c, trim=True) + ' ' + verbose_year(c), 
#                 'url'       : uri_for('Month', year=c.year, month=c.month)
#             }

#         context = {
#             'header'    : verbose_month(m) + ' <a href="' + uri_for('Year', year=y) + '">' + verbose_year(y) + '</a>',
#             'links'     : {
#                             'prev'  : _header_link(-1),
#                             'next'  : _header_link(+1)
#                           },
#             'items'     : partition(map(_info, Calendar().itermonthdates(y, m)), 7),
#             'days'      : VERBOSE_DAYS
#         }

#         render_with_context(self, 'calendar/layout/month.html', context)


# class Day(RequestHandler):
#     def get(self, year, month, day):
#         y = int(year)
#         m = int(month)
#         d = int(day)

#         update_global_date(y, m, d)

#         events = models.get_events(
#             date_min=datetime(y, m, d),
#             date_max=datetime(y, m, d)+timedelta(days=1)).order('date')

#         items = [ {
#             'time'      : verbose_time(e.date),
#             'event'     : e
#         } for e in events ]

#         def _header_link(change):
#             c = datetime(y, m, d) + timedelta(days=change)

#             return {
#                 'caption'   : verbose_day(c) + ' ' + verbose_month(c, trim=True),
#                 'url'       : uri_for('Day', year=c.year, month=c.month, day=c.day)
#             }

#         context = {
#             'header'    : verbose_day(d) + ' <a href="' + uri_for('Month', year=y, month=m) + '">' + verbose_month(m) + ' ' + verbose_year(y) + '</a>',
#             'links'     : {
#                             'prev'  : _header_link(-1),
#                             'next'  : _header_link(+1)
#                           },
#             'items'     : items,
#             'edit_key'  : self.request.get('edit'),
#             'del_key'   : self.request.get('delete'),
#             'data'      : {
#                             'hours'     : two_digits(range(0, 24)),
#                             'minutes'   : two_digits(range(0, 60, 5)),
#                           }
#         }

#         render_with_context(self, 'calendar/layout/day.html', context)

#     def post(self, year, month, day):
#         y = int(year)
#         m = int(month)
#         d = int(day)

#         t = self.request.get('submit_type')

#         uri = self.request.uri
#         uri_fix = uri.partition('?')[0]

#         if t == 'Cancel':
#             self.redirect(uri_fix)

#         elif t == 'Confirm':
#             models.Event().get(self.request.get('delete')).delete()

#             self.redirect(uri_fix)

#         else:
#             s = None

#             if t == 'Save':
#                 hh = int(self.request.get('edit_hour'))
#                 mm = int(self.request.get('edit_minute'))

#                 s = self.request.get('edit_description')
#                 e = models.Event().get(self.request.get('edit'))

#             elif t == 'Insert':
#                 hh = int(self.request.get('add_hour'))
#                 mm = int(self.request.get('add_minute'))

#                 s = self.request.get('add_description')
#                 e = models.Event()

#             if s:
#                 e.user_id = users.get_current_user().user_id()
#                 e.description = s
#                 e.date = datetime(y, m, d, hh, mm)
#                 e.put()

#                 self.redirect(uri_fix)

#             else:
#                 self.redirect(uri)