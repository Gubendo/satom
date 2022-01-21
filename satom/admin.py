from django.contrib import admin
from satom.models import Challenge

class ChallAdmin(admin.ModelAdmin):
    pass

admin.site.register(Challenge, ChallAdmin)