from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
import django.contrib.auth.views as auth_views

import core.views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', core.views.index, name='index'),
    url(r'^%s$' % settings.LOGIN_URL[1:], auth_views.login, name='login'),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
