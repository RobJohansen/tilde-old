from webapp2 import WSGIApplication, Route
import views

urls = [
    Route(
        r'/',
        handler=views.Home,
        name='Home'
    ),

    Route(
        r'/results/<query:([^/]+)?>/<tilds:([^/]+)?>',
        handler=views.Results,
        name='Results'
    ),

    Route(
        r'/tilds/<tilds:([^/]+)?>',
        handler=views.Tilds,
        name='Tilds'
    ),

    Route(
        r'/page/<page:([^/]+)?>/<timestamp:\d{14}>',
        handler=views.Page,
        name='Page'
    ),

    Route(
        r'/timeline/<tilds:([^/]+)?>',
        handler=views.Timeline,
        name='Timeline'
    ),

    Route(
        r'/derive/<id:([^/]+)?>',
        handler=views.Derive,
        name='Derive'
    ),

    Route(
        r'/seen/<id:([^/]+)?>',
        handler=views.SeenTag,
        name='SeenTag'
    ),

    Route(
        r'/seen/<year:\d{4}>/<month:\d+>/<day:\d+>/<id:([^/]+)?>',
        handler=views.SeenTime,
        name='SeenTime'
    ),

    Route(
        r'/user',
        handler=views.User,
        name='User'
    )
]

urls_admin = [
    Route(
        r'/admin/',
        handler=views.AdminConsole,
        name='AdminConsole'
    ),

    Route(
        r'/admin/push/<id:([^/]+)?>/<title:([^/]+)?>',
        handler=views.PushTask,
        name='PushTask'
    ),

    Route(
        r'/admin/add_show/<id:([^/]+)?>/<title:([^/]+)?>',
        handler=views.AddShow,
        name='AddShow'
    )
]

app = WSGIApplication(urls, debug=True)

app_admin = WSGIApplication(urls_admin, debug=True)