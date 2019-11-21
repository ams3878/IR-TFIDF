from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Character)
admin.site.register(Document)
admin.site.register(CharacterToDocument)
admin.site.register(Season)
admin.site.register(SeasonToDocument)
