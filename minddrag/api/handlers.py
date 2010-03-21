"""
These classes implement the Minddrag API.
"""

from piston.handler import AnonymousBaseHandler
from piston.handler import BaseHandler
from piston.utils import rc

from core.models import Team
from core.models import Dragable


class AnonymousTeamHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    model = Team
    fields = ('name',
              'description',
              'public',
              'created',
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


class DragableHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = Dragable
    fields = ('hash',
              ('created_by', ('username',)),
              ('team', ('name',)),
              'created',
              'updated',
              'url',
              'title',
              'text',
              'xpath',
              ('connected_to', ('hash',)),
    )


    def read(self, request, hash=None):
        username = request.user.username
        dragables = Dragable.objects.filter(team__members__username=username)

        if hash:
            dragables = dragables.filter(hash=hash)
            if not dragables:
                return rc.FORBIDDEN
        else:
            # handle optional URL parameters that must be used without 'hash'
            if 'team' in request.GET:
                dragables = dragables.filter(team__name=request.GET['team'])
                if not dragables:
                    return rc.FORBIDDEN
        
        return dragables


    def create(self, request):
        required_fields = ('hash', 'url', 'xpath')
        optional_fields = ('title', 'text', 'connected_to')

        for field in required_fields + ('team',):
            if field not in request.POST.keys():
                return rc.BAD_REQUEST # FIXME proper error msg?

        try:
            team = Team.objects.get(name=request.POST['team'])
        except:
            return rc.BAD_REQUEST     # FIXME proper error msg?

        if not team.is_member(request.user):
            return rc.FORBIDDEN       # FIXME proper error msg?

        dragable = Dragable()
        dragable.created_by = request.user
        dragable.team = team

        for field in required_fields:
            setattr(dragable, field, request.POST[field])

        for field in optional_fields:
            if field in request.POST:
                setattr(dragable, field, request.POST[field])

        dragable.save()
        return rc.CREATED


    def update(self, request, hash):
        try:
            dragable = Dragable.objects.get(hash=hash)
        except:
            return rc.BAD_REQUEST

        if not dragable.can_modify(request.user):
            return rc.FORBIDDEN

        if 'team' in request.PUT:
            try:
                team = Team.objects.get(name=request.PUT['team'])
                if not team.is_member(request.user):
                    return rc.FORBIDDEN
            except:
                return rc.BAD_REQUEST
            dragable.team = team

        if 'connected_to' in request.PUT:
            connected_to_hash = request.PUT['connected_to']
            try:
                connected_to = Dragable.objects.get(hash=connected_to_hash)
                assert dragable.team == connected_to.team # FIXME do we want to enforce this?
            except:
                return rc.BAD_REQUEST
            dragable.connected_to = connected_to

        for field in ('url', 'xpath', 'title', 'text'):
            if field in request.PUT:
                setattr(dragable, field, request.PUT[field])
        dragable.save()
        return rc.ALL_OK


    def delete(self, request, hash):
        try:
            dragable = Dragable.objects.get(hash=hash)
        except:
            return rc.BAD_REQUEST

        if not dragable.can_modify(request.user):
            return rc.FORBIDDEN

        dragable.delete()
        return rc.DELETED