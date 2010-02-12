from core import models
from django.contrib import admin

admin.site.register(models.Team)
admin.site.register(models.Dragable)
admin.site.register(models.FileAnnotation)
admin.site.register(models.ImageAnnotation)
admin.site.register(models.VideoAnnotation)
admin.site.register(models.NoteAnnotation)
admin.site.register(models.ConnectionAnnotation)
