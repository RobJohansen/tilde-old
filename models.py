from google.appengine.ext import db
from google.appengine.api import users
from datetime import datetime, timedelta

class Typde(db.Model):
    tag = db.StringListProperty()

class Tilde(db.Model):
    ancestor = db.SelfReferenceProperty(collection_name='children')
    label = db.ReferenceProperty(Typde)
    start = db.DateTimeProperty()
    end = db.DateTimeProperty()
    tag = db.StringProperty()

    def is_root(self):
        return self.label is not None

    def verbose(self, **args):
        def _verbose_rec(x, i):
            if x.is_root():
                if i == 0 and not args:
                    return x.label.key().id_or_name()

                else:
                    return x.label.tag[i].format(**args or {'tag' : '', 'key' : ''})

            else:
                return _verbose_rec(x.ancestor, i + 1)

        return _verbose_rec(self, 0)