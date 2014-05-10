from django.conf.urls import patterns, url

from tsw import views

urlpatterns = patterns('',
    url(r'^new_user/(?P<name>.+)/$', views.new_user),
    url(r'^change_name/(?P<user_id>\d+)/(?P<name>\w+)/$', views.change_name),
    #url(r'^save_score/(?P<user_id>\d+)/(?P<level>\d+)/(?P<score>\d+)/(?P<replay>.+)/$', views.save_score),
    url(r'^save_score/$', views.save_score),
    #url(r'^get_scores/(?P<user_id>\d+)/(?P<level>\d+)/$', views.get_scores),
    url(r'^get_scores/$', views.get_scores),

    url(r'^save_level/$', views.save_level),
    url(r'^get_levels/$', views.get_levels),
    url(r'^get_level/$', views.get_level),
    url(r'^rate_level/$', views.rate_level),
    url(r'^played_level/$', views.played_level),
    url(r'^completed_level/$', views.completed_level),
)