from ..user.authorization import office_auth
from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^login$', 'django.contrib.auth.views.login', {'template_name': 'user/login.html'}, name="login"),
    url(r'^logout$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name="logout"),
    url(r'^settings$', login_required(views.SettingsView.as_view()), name='settings'),
    url(r'^set_language$', views.SetLanguageView.as_view(), name='set_language'),

    url(r'^users$', office_auth(views.UserList.as_view()), name='users'),

    url(r'^add-user$', office_auth(views.UserAdd.as_view()), name='user.add'),
    url(r'^user-(?P<pk>\d+)$', office_auth(views.UserView.as_view()), name='user.view'),
    url(r'^user-(?P<pk>\d+)/edit$', office_auth(views.UserUpdate.as_view()), name='user.edit'),
    url(r'^user-(?P<pk>\d+)/remove$', office_auth(views.UserRemove.as_view()), name='user.remove'),
    url(
        r'^user-(?P<pk>\d+)/generate-password$', 
        office_auth(views.UserGeneratePassword.as_view()), name='user.generate.password'),
]
