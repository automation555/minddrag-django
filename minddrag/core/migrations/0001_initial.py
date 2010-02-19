
from south.db import db
from django.db import models
from minddrag.core.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'FileAnnotation'
        db.create_table('core_fileannotation', (
            ('id', orm['core.FileAnnotation:id']),
            ('hash', orm['core.FileAnnotation:hash']),
            ('dragable', orm['core.FileAnnotation:dragable']),
            ('creator', orm['core.FileAnnotation:creator']),
            ('created', orm['core.FileAnnotation:created']),
            ('updated', orm['core.FileAnnotation:updated']),
            ('filename', orm['core.FileAnnotation:filename']),
            ('description', orm['core.FileAnnotation:description']),
        ))
        db.send_create_signal('core', ['FileAnnotation'])
        
        # Adding model 'Dragable'
        db.create_table('core_dragable', (
            ('id', orm['core.Dragable:id']),
            ('hash', orm['core.Dragable:hash']),
            ('created_by', orm['core.Dragable:created_by']),
            ('team', orm['core.Dragable:team']),
            ('created', orm['core.Dragable:created']),
            ('updated', orm['core.Dragable:updated']),
            ('url', orm['core.Dragable:url']),
            ('title', orm['core.Dragable:title']),
            ('text', orm['core.Dragable:text']),
            ('xpath', orm['core.Dragable:xpath']),
            ('connected_to', orm['core.Dragable:connected_to']),
        ))
        db.send_create_signal('core', ['Dragable'])
        
        # Adding model 'Team'
        db.create_table('core_team', (
            ('id', orm['core.Team:id']),
            ('name', orm['core.Team:name']),
            ('description', orm['core.Team:description']),
            ('created_by', orm['core.Team:created_by']),
            ('created', orm['core.Team:created']),
            ('public', orm['core.Team:public']),
            ('password', orm['core.Team:password']),
        ))
        db.send_create_signal('core', ['Team'])
        
        # Adding model 'ImageAnnotation'
        db.create_table('core_imageannotation', (
            ('id', orm['core.ImageAnnotation:id']),
            ('hash', orm['core.ImageAnnotation:hash']),
            ('dragable', orm['core.ImageAnnotation:dragable']),
            ('creator', orm['core.ImageAnnotation:creator']),
            ('created', orm['core.ImageAnnotation:created']),
            ('updated', orm['core.ImageAnnotation:updated']),
            ('url', orm['core.ImageAnnotation:url']),
            ('description', orm['core.ImageAnnotation:description']),
        ))
        db.send_create_signal('core', ['ImageAnnotation'])
        
        # Adding model 'VideoAnnotation'
        db.create_table('core_videoannotation', (
            ('id', orm['core.VideoAnnotation:id']),
            ('hash', orm['core.VideoAnnotation:hash']),
            ('dragable', orm['core.VideoAnnotation:dragable']),
            ('creator', orm['core.VideoAnnotation:creator']),
            ('created', orm['core.VideoAnnotation:created']),
            ('updated', orm['core.VideoAnnotation:updated']),
            ('url', orm['core.VideoAnnotation:url']),
            ('description', orm['core.VideoAnnotation:description']),
            ('type', orm['core.VideoAnnotation:type']),
        ))
        db.send_create_signal('core', ['VideoAnnotation'])
        
        # Adding model 'NoteAnnotation'
        db.create_table('core_noteannotation', (
            ('id', orm['core.NoteAnnotation:id']),
            ('hash', orm['core.NoteAnnotation:hash']),
            ('dragable', orm['core.NoteAnnotation:dragable']),
            ('creator', orm['core.NoteAnnotation:creator']),
            ('created', orm['core.NoteAnnotation:created']),
            ('updated', orm['core.NoteAnnotation:updated']),
            ('text', orm['core.NoteAnnotation:text']),
        ))
        db.send_create_signal('core', ['NoteAnnotation'])
        
        # Adding model 'UrlAnnotation'
        db.create_table('core_urlannotation', (
            ('id', orm['core.UrlAnnotation:id']),
            ('hash', orm['core.UrlAnnotation:hash']),
            ('dragable', orm['core.UrlAnnotation:dragable']),
            ('creator', orm['core.UrlAnnotation:creator']),
            ('created', orm['core.UrlAnnotation:created']),
            ('updated', orm['core.UrlAnnotation:updated']),
            ('url', orm['core.UrlAnnotation:url']),
            ('description', orm['core.UrlAnnotation:description']),
        ))
        db.send_create_signal('core', ['UrlAnnotation'])
        
        # Adding model 'ConnectionAnnotation'
        db.create_table('core_connectionannotation', (
            ('id', orm['core.ConnectionAnnotation:id']),
            ('hash', orm['core.ConnectionAnnotation:hash']),
            ('dragable', orm['core.ConnectionAnnotation:dragable']),
            ('creator', orm['core.ConnectionAnnotation:creator']),
            ('created', orm['core.ConnectionAnnotation:created']),
            ('updated', orm['core.ConnectionAnnotation:updated']),
            ('connected_dragable', orm['core.ConnectionAnnotation:connected_dragable']),
        ))
        db.send_create_signal('core', ['ConnectionAnnotation'])
        
        # Adding ManyToManyField 'Team.members'
        db.create_table('core_team_members', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('team', models.ForeignKey(orm.Team, null=False)),
            ('user', models.ForeignKey(orm['auth.User'], null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'FileAnnotation'
        db.delete_table('core_fileannotation')
        
        # Deleting model 'Dragable'
        db.delete_table('core_dragable')
        
        # Deleting model 'Team'
        db.delete_table('core_team')
        
        # Deleting model 'ImageAnnotation'
        db.delete_table('core_imageannotation')
        
        # Deleting model 'VideoAnnotation'
        db.delete_table('core_videoannotation')
        
        # Deleting model 'NoteAnnotation'
        db.delete_table('core_noteannotation')
        
        # Deleting model 'UrlAnnotation'
        db.delete_table('core_urlannotation')
        
        # Deleting model 'ConnectionAnnotation'
        db.delete_table('core_connectionannotation')
        
        # Dropping ManyToManyField 'Team.members'
        db.delete_table('core_team_members')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.connectionannotation': {
            'connected_dragable': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'connected_dragable'", 'to': "orm['core.Dragable']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'dragable': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Dragable']"}),
            'hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.dragable': {
            'connected_to': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Dragable']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Team']"}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'xpath': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'core.fileannotation': {
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dragable': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Dragable']"}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.imageannotation': {
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dragable': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Dragable']"}),
            'hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'core.noteannotation': {
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'dragable': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Dragable']"}),
            'hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.team': {
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'team_created_by'", 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'core.urlannotation': {
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dragable': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Dragable']"}),
            'hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'core.videoannotation': {
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dragable': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Dragable']"}),
            'hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }
    
    complete_apps = ['core']
