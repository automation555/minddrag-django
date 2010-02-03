from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.contrib import admin
import django.contrib.auth.views as auth_views

import core.views


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', core.views.index, name='index'),
    
    url(r'^%s' % settings.LOGIN_URL[1:], auth_views.login, name='login'),
    url(r'^%s' % settings.LOGOUT_URL[1:], auth_views.logout, name='logout'),

    # django-registration
    url(r'^accounts/activate/complete/$',
        direct_to_template,
        { 'template': 'registration/activation_complete.html' },
        name='registration_activation_complete'),
    
    url(r'^accounts/activate/(?P<activation_key>\w+)/$',
        'registration.views.activate',
        { 'backend': 'registration.backends.default.DefaultBackend' },
        name='registration_activate'),

    url(r'^accounts/register/$',
        'registration.views.register',
        { 'backend': 'registration.backends.default.DefaultBackend' },
        name='registration_register'),
    
    url(r'^accounts/register/complete/$',
        direct_to_template,
        { 'template': 'registration/registration_complete.html' },
        name='registration_complete'),
    
    url(r'^accounts/register/closed/$',
        direct_to_template,
        { 'template': 'registration/registration_closed.html' },
        name='registration_disallowed'),
    
    #(r'^accounts/', include('registration.backends.default.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
         'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
