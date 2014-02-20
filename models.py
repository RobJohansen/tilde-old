from google.appengine.ext import ndb
from google.appengine.api import users
from datetime import datetime, timedelta

def current_account():
    u = users.get_current_user()

    if u:
        return Account.query().get() or Account().put().get()

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

    @property
    def children(self):
        return Tilde.query(Tilde.ancestor == self.key)

    def is_root(self):
        return self.label is not None

    def verbose(self, **args):
        def _verbose_rec(x, i):
            if x.is_root():
                if i == 0 and not args:
                    return x.label.id()

                else:
                    return x.label.get().tag[i].format(**args or {'tag' : '', 'key' : ''})

            else:
                return _verbose_rec(x.ancestor.get(), i + 1)

        return _verbose_rec(self, 0)



class Account(ndb.Model):
    user_id = ndb.StringProperty() #default=users.get_current_user().user_id())


class AccountModel(ndb.Model):
    account = ndb.KeyProperty(kind='Account')#, default=current_account().key)

    @classmethod
    def query(cls, *args, **kwds):
        return super(AccountModel, cls).query(AccountModel.account == current_account().key, *args, **kwds)


class Komple(AccountModel):
    tilde = ndb.KeyProperty(kind='Tilde')