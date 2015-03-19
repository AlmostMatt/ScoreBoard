from django.conf.urls import patterns, url

from tsw import views, scores, customlevels, graphs

urlpatterns = patterns('',
    url(r'^new_user/$', views.new_user),
    #url(r'^change_name/(?P<user_id>\d+)/(?P<name>\w+)/$', views.change_name),

    url(r'^save_score/$', scores.save_score),
    url(r'^get_scores/$', scores.get_scores),
    url(r'^flag_replay/$', scores.flag_replay),

    url(r'^server_info/$', views.server_info),
    url(r'^get_domain_update/$', views.get_domain_update),
    url(r'^log_metric/$', views.log_metric),

    url(r'^save_level/$', customlevels.save_level),
    url(r'^get_levels/$', customlevels.get_levels),
    url(r'^get_level/$', customlevels.get_level),
    url(r'^rate_level/$', customlevels.rate_level),
    url(r'^played_level/$', customlevels.played_level),
    url(r'^completed_level/$', customlevels.completed_level),

    url(r'^new_users/$', graphs.new_users),
    url(r'^domains/$', graphs.domain_distribution),
    url(r'^levels/$', graphs.level_completion),
)
