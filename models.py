from google.appengine.ext import ndb
from google.appengine.api import users
from datetime import datetime, timedelta

def current_account():
    u = users.get_current_user()

    if u:
        return Account.query(Account.user_id == u.user_id()).get() or Account().put().get()

    else:
        return None


def logout_url(uri):
    return users.create_logout_url(uri)


class Typde(ndb.Model):
    tag = ndb.StringProperty(repeated=True)


class Tilde(ndb.Model):
    ancestor = ndb.KeyProperty(kind='Tilde')
    label = ndb.KeyProperty(kind='Typde')
    start = ndb.DateTimeProperty()
    end = ndb.DateTimeProperty()
    tag = ndb.StringProperty()

    def children(self):
        return Tilde.query(Tilde.ancestor == self.key)

    def descendants(self):
        def _descendants_rec(n):
            from itertools import chain as xn

            if n:
                return [n] + list(xn(*map(_descendants_rec, n.children().order(Tilde.tag))))

            else:
                return []

        return _descendants_rec(self)

    def get_komple(self):
        return Komple.query(Komple.tilde == self.key).get()

    @property
    def is_complete(self):
        return self.get_komple() is not None

    @property
    def is_root(self):
        return self.label is not None

    def verbose(self, **args):
        def _verbose_rec(x, i):
            if x.is_root:
                v = x.label.get().tag[i].format(**args or {'tag' : self.tag, 'key' : str(self.key.id())}) 
                
                return v or x.label.id()

            else:
                return _verbose_rec(x.ancestor.get(), i + 1)

        return _verbose_rec(self, 0)

    def null_verbose(self):
        return self.verbose(tag='', key='')


    def to_calendar_node(self, selected=False):
        node = '<span>{t}</span>' + \
                '<i tag="{k}" class="btn-seen fa fa-{b}" style="float: right;"></i>'

        content = node.format(
                    k = str(self.key.id()),
                    b = 'times' if self.is_complete else 'check',
                    t = self.verbose()
        )

        className = 'node' + \
                    (' complete' if self.is_complete else '') + \
                    (' selected' if selected else '')

        return {
            'start'         : self.start,
            'end'           : self.end,
            'group'         : self.null_verbose(),
            'content'       : content,
            'className'     : className
        }

    def mark_complete(self):
        if not self.is_complete:
            Komple(tilde=self.key).put()

    def mark_incomplete(self):
        if self.is_complete:
            self.get_komple().key.delete()


class Account(ndb.Model):
    user_id = ndb.StringProperty(default=users.get_current_user().user_id())

class AccountModel(ndb.Model):
    account = ndb.KeyProperty(kind='Account', default=current_account().key)

    @classmethod
    def query(cls, *args, **kwds):
        return super(AccountModel, cls).query(AccountModel.account == current_account().key, *args, **kwds)


class Komple(AccountModel):
    tilde = ndb.KeyProperty(kind='Tilde')
    seen = ndb.DateTimeProperty()


###########
# HELPERS #
###########
def process_completion(id, d):
    n = Tilde.get_by_id(id) or Tilde.get_by_id(long(id))

    for m in n.descendants():
        if m.end <= d:
            m.mark_complete()

        else:
            m.mark_incomplete()


def get_current_tild(tilds):
    tild = None

    if not tilds == '':
        ts = tilds.split('~')

        try:
            tild = Tilde.get_by_id(ts[1])

            for (t, l) in zip(ts[2:], tild.label.get().tag[1:]):
                for c in tild.children():
                    if c.verbose() == t:
                        tild = c

        except Exception:
            pass

    return tild


def get_next_tilds(tilds):
    t = get_current_tild(tilds)

    if t:
        results = t.children()

    else:
        results = Tilde.query(Tilde.label != None).order(Tilde.label)

    return map(lambda x: {'name' : x.verbose() }, results.order(Tilde.tag))


def get_timestamp(tilds):
    t = get_current_tild(tilds)

    if t:
        timestamp = t.start

    else:
        timestamp = datetime.now()

    return timestamp.strftime('%Y%m%d%H%M%S')


def derive_tilds(id):
    m = Tilde.get_by_id(id) or Tilde.get_by_id(long(id))

    tilds = [m]

    while m.ancestor:
        m = m.ancestor.get()
        tilds.append(m)

    tilds = map(lambda x: x.verbose(), tilds)

    return tilds[::-1]