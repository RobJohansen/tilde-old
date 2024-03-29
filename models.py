from google.appengine.ext import ndb
from google.appengine.api import users
from datetime import datetime, timedelta

import tools
import logging


###########
# HELPERS #
###########

def get_current_tild(tilds):
    try:
        ts = tilds.split('~')

        n = Tilde.get_by_id(ts[1])

        for (t, l) in zip(ts[2:], n.label.get().tag[1:]):
            for c in n.children():
                if c.verbose() == t:
                    n = c

        return n

    except Exception:
        return None
        

def get_current_date(tilds):
    if tilds:
        if tilds[0] == '~':
            try:
                return tools.to_date(tilds[1:])

            except Exception:
                try:
                    return get_current_tild(tilds).start

                except Exception:
                    return None

        else:
            return None

    else:
        return None


def get_next_tilds(tilds):
    t = get_current_tild(tilds)

    if t:
        results = t.children()

    else:
        results = Tilde.query(Tilde.label != None).order(Tilde.label)

    return results.order(Tilde.tag)


def derive_tilds(id):
    m = Tilde.get_by_id(id) or Tilde.get_by_id(long(id))

    tilds = [m]

    while m.ancestor:
        m = m.ancestor.get()
        tilds.append(m)

    tilds = map(lambda x: x.verbose(), tilds)

    return tilds[::-1]




# TODO: Convert to Class Method?
# def most_complete_date(n):
#     def _next(x):
#         if x.has_komple():
#             return x

#         else:
#             t = next( (c for c in x.children().order(Tilde.start) if not c.has_komple()), None )

#             return _next(t) if t else x

#     x = _next(n.get_root())

#     return x.end if x.has_komple() else x.start


def until_date(n):
    return n.start # PLACEHOLDER 







############
# ORDERING #
############
class OrderingBase(ndb.Model):
    order = ndb.IntegerProperty(repeated=True)

    def rows(self):
        return [] # filter(lambda x: x, [Group.get_by_id(r) or Membership.get_by_id(r)  for r in self.order])


########
# USER #
########

class UserProfile(OrderingBase):
    pass


class UserModel(ndb.Model):
    @classmethod
    def __user_key(self):
        return ndb.Key(UserProfile, users.get_current_user().user_id())

    def __init__(cls, **kwargs):
        return super(UserModel, cls).__init__(parent=UserModel.__user_key(), **kwargs)

    @classmethod
    def get_by_id(cls, id, **kwargs):
        return super(UserModel, cls).get_by_id(id, parent=UserModel.__user_key(), **kwargs)

    @classmethod
    def query(cls, *args, **kwargs):
        return super(UserModel, cls).query(ancestor=UserModel.__user_key(), *args, **kwargs)


def get_user_profile():
    return UserProfile.get_or_insert(users.get_current_user().user_id())


def get_user_account():
    user = users.get_current_user()

    if user:
        user.profile = get_user_profile()

        user.is_admin = users.is_current_user_admin()
        user.logout_url = users.create_logout_url('/')
    
    return user














########
# USER #
########

# def get_user_id():
#     return users.get_current_user().user_id()


# class UserBase(ndb.Model):
#     user_id = ndb.StringProperty(default=get_user_id())


# class UserProfile(UserBase):
#     pass


# class UserModel(UserBase):
#     @classmethod
#     def query(cls, *args, **kwds):
#         return super(UserModel, cls).query(UserModel.user_id == get_user_id(), *args, **kwds)


# def get_user_profile():
#     user = users.get_current_user()

#     if user:
#         user.profile = UserProfile.query(UserProfile.user_id == user.user_id()).get() or UserProfile().put().get()

#         user.is_admin = users.is_current_user_admin()
#         user.logout_url = users.create_logout_url('/')
    
#     return user


##########
# KOMPLE #
##########
class Komple(UserModel):
    tilde = ndb.KeyProperty(kind='Tilde')


#########
# TYPDE #
#########
class Typde(ndb.Model):
    tag = ndb.StringProperty(repeated=True)


#########
# TILDE #
#########
class Tilde(ndb.Model):
    title = ndb.StringProperty()
    ancestor = ndb.KeyProperty(kind='Tilde')
    label = ndb.KeyProperty(kind='Typde')
    start = ndb.DateTimeProperty()
    end = ndb.DateTimeProperty()
    tag = ndb.StringProperty()


    ### VERBOSITY ###
    def verbose(self, **args):
        def _verbose_rec(x, i):
            if x.is_root:
                v = x.label.get().tag[i].format(**args or {
                    'tag'   : self.tag, 
                    'title' : self.title,
                    'key'   : str(self.key.id())
                }) 
                
                return v or x.label.id()

            else:
                return _verbose_rec(x.ancestor.get(), i + 1)

        return _verbose_rec(self, 0)


    def null_verbose(self):
        return self.verbose(tag='', key='', title='')


    def to_calendar_node(self, level=0):
      
        def _toRGB(p, c=0):
            return 'rgb(0, {g}, {b})'.format(
                g = str(max(255 - c if p > 50 else int(p * 5.12 - c), 0)),
                b = str(max(99 - c if p <= 50 else int(100 - c - (p - 50) * 2), 0))
            )

        p = self.percent_completed

        progress = '<div class="timeline-event-progress" ' + \
                        'style="width:{h}%;background-color:{g};border-right-color:{b};">' + \
                   '</div>'

        progress = progress.format(
                    b = _toRGB(p, 30),
                    g = _toRGB(p),
                    h = p
                )

        # TODO: ROTATE IF SMALL TIMESCALE (EPISODE) ?
        content = '<a class="timeline-event-title" level="{l}" href="#" tag="{k}">{t} {c}</a>' + \
                  '<i class="timeline-event-button fa fa-{b}" tag="{k}"></i>'

        content = content.format(
                    k = str(self.key.id()),
                    b = 'times' if self.is_complete else 'check',
                    l = level,
                    t = self.verbose(),
                    c = self.completed()
                )

        return {
            'start'         : self.start,
            'end'           : self.end,
            'group'         : self.null_verbose(),
            'content'       : progress + content,
            'className'     : None
        }


    ### RELATIONSHIPS ###
    def siblings(self, *args, **kwds):
        return Tilde.query(Tilde.ancestor == self.ancestor, Tilde.key != self.key, *args, **kwds)


    def children(self, *args, **kwds):
        return Tilde.query(Tilde.ancestor == self.key, *args, **kwds)


    def descendants(self):
        def _descendants_rec(n):
            from itertools import chain as xn

            if n:
                return [n] + list(xn(*map(_descendants_rec, n.children().order(Tilde.tag))))

            else:
                return []

        return _descendants_rec(self)


    def get_root(self):
        if self.is_root:
            return self

        else:
            return self.ancestor.get().get_root()


    @property
    def is_root(self):
        return self.ancestor is None


    ### COMPLETION ###
    @property
    def is_complete(self):
        if self.is_root:
            return self.has_komple()
            
        else:
            return self.has_komple() or self.ancestor.get().is_complete


    def get_komple(self):
        return Komple.query(Komple.tilde == self.key).get()


    def has_komple(self):
        return self.get_komple() is not None


    ### PROCESSING ###
    def mark_complete(self):
        if not self.has_komple():
            Komple(tilde=self.key).put()


    def unmark_complete(self):
        if self.has_komple():
            self.get_komple().key.delete()


    def process_completion(self):
        n = self
        ns = n.siblings()

        while ns.count() > 0 and all(map(lambda m: m.is_complete, ns)):
            n = n.ancestor.get()
            ns = n.siblings()

        map(lambda m: m.unmark_complete(), n.descendants())
        n.mark_complete()


    def process_uncompletion(self):
        n = self
        ns = n.siblings()

        map(lambda m: m.unmark_complete(), n.descendants())
        n.unmark_complete()

        while ns.count() > 0 and n.is_complete:
            map(lambda m: m.mark_complete(), ns)

            n = n.ancestor.get()
            ns = n.siblings()

            n.unmark_complete()


    def process_check(self, date):
        pass
        # if self.end > date:
        #     self.process_uncompletion()

        # else:
        #     self.process_completion()

        # for c in self.children():
        #     c.process_check(date)


    ### PERCENTAGES ###
    @property
    def percent_completed(self):
        return 100 if self.is_complete else 0

        # if self.num_children == 0:
        #     if self.is_complete:
        #         return 100

        #     else:
        #         return 0

        # else:
        #     return self.num_completed / self.num_children * 100

    def completed(self):
        return ''
        
        # if self.is_complete:
        #     return ''

        # else:
        #     return '({c} / {t})'.format(
        #         c=str(self.num_completed),
        #         t=str(self.num_children)
        #     )

    @property
    def num_completed(self):
        return 0

        # return len(filter(lambda m: m.is_complete, self.children()))

    @property
    def num_children(self):
        return 0

        # return self.children().count()
