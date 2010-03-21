'''
Created on Feb 27, 2010

URL configuration for the Minddrag API

@author: hs
'''

from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from api.handlers import TeamHandler
from api.handlers import DragableHandler

auth = HttpBasicAuthentication(realm='Minddrag API')
ad = { 'authentication': auth }

team_resource = Resource(handler=TeamHandler, **ad)
dragable_resource = Resource(handler=DragableHandler, **ad)

urlpatterns = patterns('',
    url(r'^teams/$', team_resource, name='api_teams'),
    url(r'^teams/(?P<name>[^/]+)/$', team_resource, name='api_teams_by_name'),
    url(r'^dragables/$', dragable_resource, name='api_dragables'),
    url(r'^dragables/(?P<hash>[^/]+)/$',
        dragable_resource, name='api_dragables_by_hash'),
)

