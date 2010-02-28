'''
Created on Feb 27, 2010

URL configuration for the Minddrag API

@author: hs
'''

from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from api.handlers import TeamHandler

auth = HttpBasicAuthentication(realm='Minddrag API')
ad = { 'authentication': auth }

team_resource = Resource(handler=TeamHandler, **ad)

urlpatterns = patterns('',
    url(r'^teams/$', team_resource, name='api_teams'),
    url(r'^teams/(?P<name>[^/]+)/$', team_resource, name='api_teams_by_name'),
)