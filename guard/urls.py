from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'guard.views.home', name='home'),
    url(r'^polls/', include('polls.urls')),
    url(r'^tsw/', include('tsw.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
