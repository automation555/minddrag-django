from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.contrib import admin
import django.contrib.auth.views as auth_views

import core.views


admin.autodiscover()

ACCPREF = settings.ACCOUNTS_URL_PREFIX[1:]

urlpatterns = patterns('',
    url(r'^$', core.views.index, name='index'),

    url(r'^%s' % settings.LOGIN_URL[1:], auth_views.login, name='auth_login'),
    url(r'^%s' % settings.LOGOUT_URL[1:], auth_views.logout, name='auth_logout'),

    url(r'^%s$' % (ACCPREF + 'password_change/'),
        auth_views.password_change,
        name='auth_password_change'),

    url(r'^%s$' % (ACCPREF + 'password_change/done/'),
        auth_views.password_change_done,
        name='auth_password_change_done'),

    url(r'^%s$' % (ACCPREF + 'password_reset/'),
        auth_views.password_reset,
        name='auth_password_reset'),

    url(r'^%s$' % (ACCPREF + 'password_reset/done/'),
        auth_views.password_reset_done,
        name='auth_password_reset_done'),

    url(r'^%s$' % (ACCPREF + 'reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/'),
        auth_views.password_reset_confirm,
        name='auth_password_reset_confirm'),

    url(r'^%s$' % (ACCPREF + 'reset/done/'),
        auth_views.password_reset_complete,
        name='auth_password_reset_complete'),


    # django-registration
    url(r'^%s$' % (ACCPREF + 'activate/complete/'),
        direct_to_template,
        { 'template': 'registration/activation_complete.html' },
        name='registration_activation_complete'),

    url(r'^%s$' % (ACCPREF + 'activate/(?P<activation_key>\w+)/'),
        'registration.views.activate',
        { 'backend': 'registration.backends.default.DefaultBackend' },
        name='registration_activate'),

    url(r'^%s$' % (ACCPREF + 'register/'),
        'registration.views.register',
        { 'backend': 'registration.backends.default.DefaultBackend' },
        name='registration_register'),

    url(r'^%s$' % (ACCPREF + 'register/complete/'),
        direct_to_template,
        { 'template': 'registration/registration_complete.html' },
        name='registration_complete'),

#    url(r'^accounts/register/closed/$',
#        direct_to_template,
#        { 'template': 'registration/registration_closed.html' },
#        name='registration_disallowed'),

    url(r'^members/$', 'core.views.my_dragables', name='core_my_dragables'),

    # API
    (r'^api/1.0/', include('api.urls')),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
         'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
