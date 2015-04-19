from django.conf.urls import patterns, url
from app import views

# Third parameter is optional for identification purposes
urlpatterns = patterns('',
    # Site home
    url(r'^$', views.home, name='home'),
    # Credential management
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^user/(?P<user_name_slug>[\w\-]+)/delete_account/$', views.delete_account, name='delete account'),
    # User homepage
    url(r'^user/(?P<user_name_slug>[\w\-]+)/$', views.user, name='user'),
    url(r'^user/(?P<user_name_slug>[\w\-]+)/folder/(?P<folder_slug>[\w\-]+)/$', views.folder, name='folder'),
    url(r'^user/(?P<user_name_slug>[\w\-]+)/add_folder/$', views.add_folder, name='add folder'),
    url(r'^user/(?P<user_name_slug>[\w\-]+)/folder/(?P<folder_slug>[\w\-]+)/delete/$', views.delete_folder, name='delete folder'),
    # Group homepage
    url(r'^group/(?P<group_id>[\w\-]+)/$', views.group, name='group'),
    url(r'^add_group/$', views.add_group, name='add_group'),
    url(r'^group/(?P<group_id>[\w\-]+)/add_to_group/$', views.add_to_group, name='add to group'),
    url(r'^group/(?P<group_id>[\w\-]+)/remove_from_group/$', views.remove_from_group, name='remove from group'),
    url(r'^user/(?P<user_name_slug>[\w\-]+)/report/(?P<report_slug>[\w\-]+)/share/$', views.share_report, name='share report'),
    url(r'^group/(?P<group_id>[\w\-]+)/report/(?P<report_slug>[\w\-]+)/remove/$', views.remove_report, name='remove report'),
    # Reports
    url(r'^report/(?P<report_slug>[\w\-]+)/$', views.report, name='view report'),
    url(r'^user/(?P<user_name_slug>[\w\-]+)/add_report/$', views.add_report, name='report'),
    url(r'^user/(?P<user_name_slug>[\w\-]+)/folder/(?P<folder_slug>[\w\-]+)/add_report/$', views.add_report, name='report'),
    url(r'^user/(?P<user_name_slug>[\w\-]+)/report/(?P<report_slug>[\w\-]+)/edit/$', views.edit_report, name='edit report'),
    url(r'^user/(?P<user_name_slug>[\w\-]+)/report/(?P<report_slug>[\w\-]+)/copy/$', views.copy_report, name='copy report'),
    url(r'^user/(?P<user_name_slug>[\w\-]+)/report/(?P<report_slug>[\w\-]+)/move/$', views.move_report, name='move report'),
    url(r'^user/(?P<user_name_slug>[\w\-]+)/report/(?P<report_slug>[\w\-]+)/delete$', views.delete_report, name='delete report'),
    url(r'^report/(?P<report_slug>[\w\-]+)/files/$', views.add_file, name='add file'),
    url(r'^report/(?P<report_slug>[\w\-]+)/files/(?P<file_slug>[\w\-]+)/delete/$', views.delete_file, name='delete file'),
    # Search
    url(r'^search/$', views.search, name='search'),
    # Group Access
    url(r'^request-group-access/$', views.group_request, name='request group access'),
    url(r'^view-group-requests/$', views.view_group_requests, name='view group requests'),
    url(r'^request/(?P<request_id>[\w\-]+)/confirm/$', views.confirm_request, name='confirm request'),
    url(r'^request/(?P<request_id>[\w\-]+)/delete/$', views.delete_request, name='delete request'),
)
