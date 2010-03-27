"""
These classes implement the Minddrag API.
"""

from piston.handler import AnonymousBaseHandler
from piston.handler import BaseHandler
from piston.utils import rc

from core.models import Team
from core.models import Dragable
from core.models import Annotation

class AnonymousTeamHandler(AnonymousBaseHandler):
    allowed_methods = ('GET',)
    model = Team
    fields = (
        'name',
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
    fields = (
        'name',
        'description',
        'public',
        'created',
        ('created_by', ('username',)),
        ('members', ('username',)),
    )
    exclude = ('password',)

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
    fields = (
        'hash',
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

        if hash:
            dragables = Dragable.objects.filter(hash=hash)
            if not dragables.count():
                return rc.BAD_REQUEST
            else:
                dragables = dragables.filter(team__members__username=username)
                if not dragables.count():
                    return rc.FORBIDDEN
        else:
            dragables = Dragable.objects.filter(
                                            team__members__username=username)
            # handle optional URL parameters that must be used without 'hash'
            if 'team' in request.GET:
                dragables = dragables.filter(team__name=request.GET['team'])
                if not dragables.count():
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


class AnnotationHandler(BaseHandler):
    allowed_methods = ('GET', 'POST',)# 'PUT', 'DELETE')
    model = Annotation
    fields = (
        'hash',
        ('dragable', ('hash',)),
        ('created_by', ('username',)),
        'created',
        'updated',
        'type',
        'note',
        'url',
        'description',
        ('connected_dragable', 'hash'),
    )
    exclude = ('filename',)


    def read(self, request, hash=None):
        username = request.user.username

        if hash:
            annotations = Annotation.objects.filter(hash=hash)
            if not annotations.count():
                return rc.BAD_REQUEST
            else:
                annotations = annotations.filter(
                                dragable__team__members__username=username)
                if not annotations.count():
                    return rc.FORBIDDEN
        else:
            annotations = Annotation.objects.filter(
                            dragable__team__members__username=username)
            if 'dragable' in request.GET:
                dragable_hash = request.GET['dragable']
                annotations = annotations.filter(dragable__hash=dragable_hash)
                if not annotations.count():
                    return rc.BAD_REQUEST

        return annotations


    def create(self, request):
        required_fields = ('hash', 'dragable', 'type')
        for field in required_fields:
            if field not in request.POST:
                return rc.BAD_REQUEST

        type = request.POST['type']
        if type == 'note':
            return self._create_note_annotation(request)
        elif type == 'url':
            return self._create_url_annotation(request)
        elif type == 'image':
            return self._create_image_annotation(request)
        elif type == 'video':
            return self._create_video_annotation(request)
        elif type == 'file':
            return self._create_file_annotation(request)
        elif type == 'connection':
            return self._create_connection_annotation(request)
        else:
            return rc.BAD_REQUEST


    def _create_note_annotation(self, request):
        qdict = request.POST

        if (Annotation.objects.filter(hash=qdict['hash']).count()):
            return rc.BAD_REQUEST

        try:
            annotation = self._create_with_common_fields(request)
            annotation.note = qdict['note']
            annotation.save()
        except:
            return rc.BAD_REQUEST

        return rc.CREATED


    def _create_url_annotation(self, request):
        qdict = request.POST

        if (Annotation.objects.filter(hash=qdict['hash']).count()):
            return rc.BAD_REQUEST

        try:
            annotation = self._create_with_common_fields(request)
            annotation.url = qdict['url']
            if 'description' in qdict:
                annotation.description = qdict['description']
            annotation.save()
        except:
            return rc.BAD_REQUEST

        return rc.CREATED


    def _create_image_annotation(self, request):
        # for now, the same as url annotation
        return self._create_url_annotation(request)


    def _create_video_annotation(self, request):
        # for now, the same as url annotation
        return self._create_url_annotation(request)


    def _create_file_annotation(self, request):
        # for now, the same as url annotation
        return self._create_url_annotation(request)


    def _create_connection_annotation(self, request):
        qdict = request.POST
        if (qdict['dragable'] == qdict['connected_to']):
            return rc.BAD_REQUEST

        if (Annotation.objects.filter(hash=qdict['hash']).count()):
            return rc.BAD_REQUEST

        try:
            annotation = self._create_with_common_fields(request)
            connected_to = Dragable.objects.get(hash=qdict['connected_to'])
            annotation.connected_dragable = connected_to
            annotation.save()
        except:
            return rc.BAD_REQUEST

        return rc.CREATED


    def _create_with_common_fields(self, request):
        qdict = request.POST
        dragable = Dragable.objects.get(hash=qdict['dragable'])
        annotation = Annotation()
        annotation.dragable = dragable
        annotation.created_by = request.user

        for field in ('hash', 'type'):
            setattr(annotation, field, qdict[field])

        return annotation
