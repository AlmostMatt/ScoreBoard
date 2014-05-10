from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^$', 'guard.views.home', name='home'),
#    url(r'^crossdomain.xml$',
#    'flashpolicies.views.simple',
#    {'domains': ['*']}),
    url(r'^tsw/', include('tsw.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
