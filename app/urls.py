from django.conf.urls import patterns, url
from app import views

# Third parameter is optional for identification purposes
urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^user/(?P<user_name_slug>[\w\-]+)/delete_account/$', views.delete_account, name='delete account'),
    url(r'^user/(?P<user_name_slug>[\w\-]+)/$', views.user, name='user'),
    url(r'^user/(?P<user_name_slug>[\w\-]+)/add_report/$', views.add_report, name='add report'),
)
