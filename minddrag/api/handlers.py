"""
These classes implement the Minddrag API.
"""

from piston.handler import AnonymousBaseHandler
from piston.handler import BaseHandler
from piston.utils import rc

from core.models import Team


class AnonymousTeamHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    model = Team
    fields = ('name',
              'description',
              'public',
              ('created_by', ('username',)),
              ('members', ('username',)),
    )
    exclude = ('password',)


class TeamHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = Team
    anonymous = AnonymousTeamHandler
    
    def create(self, request):
        if not 'name' in request.POST:
            return rc.BAD_REQUEST

        if Team.objects.filter(name=request.POST['name']):
            return rc.DUPLICATE_ENTRY
        
        data = {}        
        data['name'] = request.POST['name']
        data['created_by'] = request.user

        if 'description' in request.POST:
            data['description'] = request.POST['description']

        if 'password' in request.POST and request.POST['password'].strip():
            data['public'] = False
            data['password'] = request.POST['password']
        
        team = Team(**data)
        team.save()
        return rc.CREATED
    
    
    def update(self, request, name):
        try:
            team = Team.objects.get(name=name)
        except:
            return rc.BAD_REQUEST
        
        if team.created_by != request.user:
            return rc.FORBIDDEN
        
        if 'name' in request.PUT:
            team.name = request.PUT['name']

        if 'description' in request.PUT:
            team.description = request.PUT['description']
            
        if 'password' in request.PUT and request.PUT['password'].strip():
            team.public = False
            team.password = request.PUT['password']
        
        team.save()
        return rc.ALL_OK


    def delete(self, request, name):
        try:
            team = Team.objects.get(name=name)
        except:
            return rc.BAD_REQUEST
        
        if team.created_by != request.user:
            return rc.FORBIDDEN
        
        team.delete()
        return rc.DELETED
