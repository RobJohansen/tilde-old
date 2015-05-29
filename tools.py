import models
import jinja2
import os
import json

from datetime import datetime, timedelta, date

def render_to_string(filename, context={ }):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

    template = env.get_template('templates/' + filename)

    return template.render(context)


def render_with_context(self, filename, context={ }):
    context.update({
        'user'  : models.get_user_account()
    })

    output = render_to_string(filename, context)

    self.response.out.write(output)


def json_response(self, context):
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(context))




DATE_FORMAT = '%Y%m%d'

TIME_FORMAT = '%H%M%S'

JSON_FORMAT = '%Y-%m-%d'

VERBOSE_FORMAT = '%d %b %Y'


def to_date(t):
    return '' if not t else datetime.strptime(t, DATE_FORMAT)


def to_timestamp(d):
    return '' if not d else d.strftime(DATE_FORMAT)


def to_json_date(d):
    return '' if not d else d.strftime(JSON_FORMAT)


def to_verbose(t=None, d=None):
    if t:
        return to_date(t).strftime(VERBOSE_FORMAT)

    elif d:
        return d.strftime(VERBOSE_FORMAT)

    else:
        return ''