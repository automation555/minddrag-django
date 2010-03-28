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


    def is_member(self, user):
        return self.members.filter(username=user.username)


    def save(self, *args, **kwargs):
        super(Team, self).save(*args, **kwargs)
        self.members.add(self.created_by)


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


    def can_modify(self, user):
        """
        Returns true, if the user created the dragable, or is a member of
        the team the dragable belongs to.
        """
        return (self.created_by == user) or self.team.is_member(user)


    def __unicode__(self):
        return self.hash


class Annotation(models.Model):
    """
    Information that a user added to a dragable.
    There are 6 types of annotations that use different fields of this model.
    """
    TYPE_CHOICES = (
        (u'note', _('Note')),
        (u'url', _('URL')),
        (u'image', _('Image')),
        (u'video', _('Video')),
        (u'file', _('File')),
        (u'connection', _('Connection')),
    )

    class Meta:
        verbose_name = _('annotation')
        verbose_name_plural = _('annotations')
        ordering = ['created']

    # common fields
    hash = models.CharField(_('hash'), max_length=128, unique=True)
    dragable = models.ForeignKey(Dragable, name=_('dragable'))
    created_by = models.ForeignKey(User, name=_('created_by'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    type = models.CharField(_('type'), max_length=32, choices=TYPE_CHOICES)
    # note annotation field
    note = models.TextField(_('note'), blank=True)
    # url/image/video annotation fields
    url = models.URLField(_('URL'), verify_exists=False, blank=True)
    description = models.TextField(_('description'), blank=True)
    # file annotation field
    filename = models.CharField(_('filename'), max_length=255, blank=True)
    # connection annotation field
    connected_dragable = models.ForeignKey(Dragable,
                                           name=_('connected dragable'),
                                           related_name='connected_dragable',
                                           blank=True,
                                           null=True)

    def __unicode__(self):
        return self.hash
