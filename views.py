from google.appengine.api import users, datastore_errors
from webapp2 import RequestHandler, uri_for
from datetime import datetime, timedelta, date

import jinja2
import os
import json
import logging

import models
import views_page


###########
# HELPERS #
###########


def render_to_string(filename, context={ }):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

    template = env.get_template(filename)

    return template.render(context)


def render_with_context(self, filename, context={ }):
    from google.appengine.api import users

    context.update({
        'user'              : models.get_user_account(),
        'empty_page_url'    : ''#uri_for('PageEmpty')
    })

    output = render_to_string('templates/' + filename, context)

    self.response.out.write(output)


def json_response(self, context):
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(context))


def json_date(d):
    return d.strftime("%Y-%m-%d")












# class DummyPage(RequestHandler):
#     def get(self, terms, tilds=None):
#         context = {
#             'terms'     : terms,
#             'tilds'     : tilds,
#             'date'      : '2015-10-01'
#         }

#         content = '' #render_to_string('templates/dummy_page.html', context)

#         context.update({
#             'content'   : content,
#         })

#         json_response(self, context)


class Demo(RequestHandler):
    def get(self, terms, tilds=None):
        timestamp = models.get_current_timestamp(tilds)

        context = {
            'terms'     : terms,
            'tilds'     : tilds,
            'date'      : timestamp
        }

        render_with_context(self, 'demo.html', context)


class DemoHome(RequestHandler):
    def get(self):
        render_with_context(self, 'demo.html', { })


################
# VIEWS : HTML #
################

class Page(RequestHandler):
    def get(self, terms, tilds=None):
        timestamp = models.get_current_timestamp(tilds)

        results = views_page.search(terms, timestamp)

        logging.debug('PageRender : timestamp = ' + str(timestamp) + ' : results = ' + str(len(results)))

        context = {
            'terms' : terms,
            'tilds' : tilds
        }

        if len(results) == 1:
            content = views_page.render(**results[0])

        else:
            content = render_to_string('templates/page_results.html', {
                'results'   : results,
                'terms'     : terms
            })
            
        context.update({
            'content'   : content
        })

        json_response(self, context)


class PageEmpty(RequestHandler):
    def get(self):
        render_with_context(self, 'page_empty.html')















#####################
# VIEWS : TEMPLATES #
#####################
class Home(RequestHandler):
    def get(self):
        tilds = [ t for t in self.request.get('ts').split('~') if len(t) > 0 ]

        context = {
            'tilds'     : tilds
        }

        render_with_context(self, 'home.html', context)


class User(RequestHandler):
    def get(self):
        context = {

        }

        render_with_context(self, 'user.html', context)


class AdminConsole(RequestHandler):
    def get(self):
        context = {

        }

        render_with_context(self, 'admin.html', context)



######################
# VIEWS : BLOODHOUND #
######################
class Tilds(RequestHandler):
    def get(self, tilds):
        context = models.get_next_tilds(tilds)

        json_response(self, context)
            



################
# VIEWS : JSON #
################
class Timeline(RequestHandler):
    def get(self, tilds):
        context = { 'success' : True }

        try:
            n = models.get_current_tild(tilds)

            results = []

            if n:
                # RESULTS
                if n.ancestor:
                    m = n.ancestor.get()
                    results.append((m, 0))
                    results.extend([(c, 1) for c in m.children() if not n.key == c.key])

                results.append((n, 1))
                results.extend([(c, 2) for c in n.children()])

                results = [n.to_calendar_node(level=l) for (n, l) in results]

                # UNTIL DATE PLACEHOLDER
                # results.append({
                #     'start'         : results[0]['start'],
                #     'end'           : None,
                #     'group'         : None,
                #     'content'       : None,
                #     'className'     : None
                # })

                # BOUNDARIES
                # diff = max((n.end - n.start) / 10, timedelta(days=1))

                # context.update({
                #     'min'       : json_date(n.start - diff),
                #     'max'       : json_date(n.end + diff)
                # })

            from gviz_api import DataTable

            table = DataTable({
                'start'     : ('date', 'Start'),
                'end'       : ('date', 'End'),
                'content'   : ('string', 'Content'),
                'group'     : ('string', 'Group'),
                'className' : ('string', 'Class')
            })

            table.LoadData(results)

            context['data'] = table.ToJSon()

        except Exception as e:
            context['success'] = False
            context['error'] = str(e)

        finally:
            json_response(self, context)


class Derive(RequestHandler):
    def get(self, id):
        context = { 'success' : True }

        try:
            tilds = models.derive_tilds(id)

            context['tilds'] = tilds

        except Exception as e:
            context['success'] = False
            context['error'] = str(e)

        finally:
            json_response(self, context)


class SeenTag(RequestHandler):
    def post(self, id):
        context = { 'success' : True }

        try:
            n = models.Tilde.get_by_id(id) or models.Tilde.get_by_id(long(id))

            if n.is_complete:
                n.process_uncompletion()

            else:
                n.process_completion()

        except Exception as e:
            context['success'] = False
            context['error'] = str(e)

        finally:
            json_response(self, context)


class SeenTime(RequestHandler):
    def post(self, year, month, day, id):
        context = { 'success' : True }

        try:
            id = id.split('~')[1]
            n = models.Tilde.get_by_id(id) or models.Tilde.get_by_id(long(id))

            n.process_check(datetime(long(year), long(month), long(day)))

        except Exception as e:
            context['success'] = False
            context['error'] = str(e)

        finally:
            json_response(self, context)











# /0285331/24
# /0285333/Alias
# /0411008/Lost
# /0944947/Game of Thrones
# /0804503/Mad Men
class PushTask(RequestHandler):
    def get(self, id, title):
        from google.appengine.api import taskqueue

        taskqueue.add(url='/admin/add_show/' + str(id) + '/' + str(title))
        self.response.write('Task Added')


class AddShow(RequestHandler):
    def post(self, id, title):
        typde_name = 'Show'

        import logging

        from imdb import IMDb
        from imdb.helpers import sortedSeasons, sortedEpisodes

        def parse_date(d):
            try:
                return datetime.strptime(d.replace('.', ''), '%d %b %Y')

            except Exception:
                return datetime.strptime(d.replace('.', ''), '%b %Y')

        i = IMDb()
        m = i.get_movie(id)
        i.update(m, 'episodes')

        t = models.Typde.get_by_id(typde_name)

        show = models.Tilde(id=str(m.get('title', title)), label=t.key)
        show.start = parse_date(m['episodes'][1][1]['original air date'])
        show.put()
        
        seasons = sortedSeasons(m)

        for s in seasons:
            if s > 0:
                episodes = sortedEpisodes(m, season=s)

                start_date = parse_date(episodes[0]['original air date'])

                season = models.Tilde(ancestor=show.key)
                season.start = start_date
                season.tag = str(s)
                season.put()

                for (e, i) in zip(episodes, range(1, 100)):
                    start_date = parse_date(e['original air date'])
                    end_date = start_date + timedelta(days=1)

                    episode = models.Tilde(ancestor=season.key)
                    episode.start = start_date
                    episode.end = end_date
                    episode.tag = str(i)
                    episode.title = e['title']
                    episode.put()

                season.end = end_date
                season.put()

        show.end = end_date
        show.put()





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

