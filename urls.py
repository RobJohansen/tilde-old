from webapp2 import WSGIApplication, Route
import views

urls = [


    Route(
        r'/d/<tilds:~([^/]+)?>',
        handler='views.Date:get_json',
        name='JsonDate'
    ),

    Route(
        r'/r/<timestamp:([^/]+)?>/<page_id:([^/]+)?>/<rev_id:([^/]+)?>',
        handler=views.Render,
        name='Render'
    ),

    Route(
        r'/p/<timestamp:([^/]+)?>/<terms:([^/^~]+)?><tilds:(~[^/]+)?>',
        handler=views.Page,
        name='Page'
    ),





    Route(
        r'/<terms:([^/^~]+)?><tilds:(~[^/]+)?>',
        handler=views.Base,
        name='Base'
    ),

    Route(
        r'/<terms:([^/^~]+)?>',
        handler=views.Base,
        name='BaseLatest'
    ),

    Route(
        r'/',
        handler=views.Base,
        name='BaseNull'
    ),







    # Route(
    #     r'/',
    #     handler=views.Home,
    #     name='Home'
    # ),



    # Route(
    #     r'/dummy/<terms:([^/]+)?>/<tilds:([^/]+)?>',
    #     handler=views.DummyPage,
    #     name='DummyPage'
    # ),





    Route(
        r'/t/<tilds:([^/]+)?>',
        handler=views.Tilds,
        name='Tilds'
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