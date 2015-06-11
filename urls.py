from webapp2 import WSGIApplication, Route
import views

urls = [
    Route(
        r'/get_terms/<terms:([^/]+)?>',
        handler='views.GetTerms:get_json'
    ),

    Route(
        r'/get_tilds/<tilds:([^/]+)?>',
        handler='views.GetTilds:get_json'
    ),

    Route(
        r'/date/<tilds:([^/]+)?>',
        handler='views.Date:get_json'
    ),

    Route(
        r'/derive/<id:([^/]+)?>',
        handler='views.Derive:get_json'
    ),

    Route(
        r'/timeline/<tilds:([^/]+)?>',
        handler='views.Timeline:get_json'
    ),






    Route(
        r'/page/<terms:([^/^~]+)?><tilds:(~[^/]+)?>',
        handler=views.Page,
        name='Page'
    ),

    Route(
        r'/render/<rev_id:\d+>',
        handler=views.Render,
        name='Render'
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
    #     r'/seen/<id:([^/]+)?>',
    #     handler=views.SeenTag,
    #     name='SeenTag'
    # ),

    # Route(
    #     r'/seen/<year:\d{4}>/<month:\d+>/<day:\d+>/<id:([^/]+)?>',
    #     handler=views.SeenTime,
    #     name='SeenTime'
    # ),

    # Route(
    #     r'/user',
    #     handler=views.User,
    #     name='User'
    # )
]

urls_admin = [
    # Route(
    #     r'/admin/',
    #     handler=views.AdminConsole,
    #     name='AdminConsole'
    # ),

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