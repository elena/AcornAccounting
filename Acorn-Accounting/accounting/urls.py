from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'accounts.views.show_accounts_chart', name='homepage'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^entries/', include('entries.urls')),
    url(r'^events/', include('events.urls')),
    url(r'^fiscalyears/', include('fiscalyears.urls')),
)

urlpatterns += staticfiles_urlpatterns()
