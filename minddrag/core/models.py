"""
Models for the core app
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Team(models.Model):
    """
    Teams can work together on dragables either in public or in private.
    """
    class Meta:
        verbose_name = _('team')
        verbose_name_plural = _('teams')
        ordering = ['name', 'created']
        
    name = models.CharField(_('name'), max_length=64, unique=True)
    description = models.TextField(_('description'), blank=True)
    created_by = models.ForeignKey(User,
                                   name=_('created by'),
                                   related_name='team_created_by')
    members = models.ManyToManyField(User,
                                     name=_('members'),
                                     related_name='team_members',
                                     null=True,
                                     blank=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    public = models.BooleanField(_('public'), default=True)
    password = models.CharField(_('password'), max_length=128, blank=True)


    def has_access(self, user):
        """
        Returns true, if the team is public, or the given user is the founder
        or a member of the team.
        """
        return self.public or self.founder == user or self.members.contains(
                                                                        user)

         
    def __unicode__(self):
        return self.name
        

class Dragable(models.Model):
    """
    A piece of information from the web that can be dragged into minddrag.
    """
    class Meta:
        verbose_name = _('dragable')
        verbose_name_plural = _('dragables')
        ordering = ['created']
        
    hash = models.CharField(_('hash'), max_length=128, unique=True)
    created_by = models.ForeignKey(User, name=_('created by'))
    team = models.ForeignKey(Team, name=_('team'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    url = models.URLField(_('URL'), verify_exists=False)
    title = models.CharField(_('title'), max_length=255, blank=True)
    text = models.TextField(_('text'), blank=True)
    xpath = models.TextField(_('xpath'), blank=True)
    connected_to = models.ForeignKey('self',
                                     name=_('connected to'),
                                     blank=True,
                                     null=True)

    def __unicode__(self):
        return self.hash


class Annotation(models.Model):
    """
    Information that a user added to a dragable.
    This is an abstract base class for all types of annotations.
    """
    class Meta:
        verbose_name = _('annotation')
        verbose_name_plural = _('annotations')
        ordering = ['created']
        abstract = True
    
    hash = models.CharField(_('hash'), max_length=128, unique=True)
    dragable = models.ForeignKey(Dragable, name=_('dragable'))
    creator = models.ForeignKey(User, name=_('creator'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    def __unicode__(self):
        return self.hash


class NoteAnnotation(Annotation):
    """
    Annotate a dragable with some text written by the user.
    """
    class Meta:
        verbose_name = _('note annotation')
        verbose_name_plural = _('note annotations')
    
    text = models.TextField(_('text'))


class UrlAnnotation(Annotation):
    """
    Annotate a dragable with a link to a website.
    """
    class Meta:
        verbose_name = _('URL annotation')
        verbose_name_plural = _('URL annotations')
    
    url = models.URLField(_('URL'), verify_exists=False)
    description = models.TextField(_('description'), blank=True)


class ImageAnnotation(Annotation):
    """
    Annotate a dragable with an image from the web.
    """
    class Meta:
        verbose_name = _('image annotation')
        verbose_name_plural = _('image annotations')
    
    url = models.URLField(_('URL'), verify_exists=False)
    description = models.TextField(_('description'), blank=True)


class VideoAnnotation(Annotation):
    """
    Annotate a dragable with a video from the web.
    """
    class Meta:
        verbose_name = _('video annotation')
        verbose_name_plural = _('video annotations')

    url = models.URLField(_('URL'), verify_exists=False)
    description = models.TextField(_('description'), blank=True)
    type = models.CharField(_('video type'), max_length=32, blank=True) # maybe youtube, vimeo, etc.


class FileAnnotation(Annotation):
    """
    Annotate a dragable with a file uploaded by the user.
    """
    class Meta:
        verbose_name = _('file annotation')
        verbose_name_plural = _('file annotations')

    filename = models.CharField(_('filename'), max_length=255)
    description = models.TextField(_('description'), blank=True)


class ConnectionAnnotation(Annotation):
    """
    Annotate a dragable with another dragable, i.e. connect dragables.
    """
    class Meta:
        verbose_name = _('connection annotation')
        verbose_name_plural = _('connection annotations')

    connected_dragable = models.ForeignKey(Dragable,
                                           name=_('connected dragable'),
                                           related_name='connected_dragable')
