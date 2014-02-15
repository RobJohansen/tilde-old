from webapp2 import WSGIApplication, Route
import views as v

urls = [
    Route(
        r'/',
        handler=v.Home,
        name='Home'
    ),

    Route(
        r'/results',
        handler=v.Results,
        name='Results'
    ),

    Route(
        r'/do',
        handler=v.DoStuff,
        name='DoStuff'
    ),

    Route(
        r'/test',
        handler=v.Test,
        name='Test'
    )
]

app = WSGIApplication(urls, debug=True)