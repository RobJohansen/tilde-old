from webapp2 import WSGIApplication, Route
import views as v

urls = [
    Route(
        r'/',
        handler=v.Home,
        name='Home'
    ),

    Route(
        r'/results/<query:([^/]+)?>/<tilds:([^/]+)?>',
        handler=v.Results,
        name='Results'
    ),

    Route(
        r'/tilds/<tilds:([^/]+)?>',
        handler=v.Tilds,
        name='Tilds'
    ),

    Route(
        r'/page/<page:([^/]+)?>/<timestamp:\d{14}>',
        handler=v.Page,
        name='Page'
    ),

    Route(
        r'/timeline/<tilds:([^/]+)?>',
        handler=v.Timeline,
        name='Timeline'
    ),

    Route(
        r'/derive/<id:([^/]+)?>',
        handler=v.Derive,
        name='Derive'
    ),

    Route(
        r'/seen/<id:([^/]+)?>',
        handler=v.SeenTag,
        name='SeenTag'
    ),

    Route(
        r'/seen/<id:([^/]+)?>/<year:\d{4}>/<month:\d+>/<day:\d+>',
        handler=v.SeenTime,
        name='SeenTime'
    ),



    Route(
        r'/test',
        handler=v.Test,
        name='Test'
    )

]

app = WSGIApplication(urls, debug=True)