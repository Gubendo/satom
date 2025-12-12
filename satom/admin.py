from django.contrib import admin
from satom.models import Challenge, MotPossible

class ChallAdmin(admin.ModelAdmin):
    pass

class MotPossibleAdmin(admin.ModelAdmin):
    pass

admin.site.register(Challenge, ChallAdmin)
admin.site.register(MotPossible, MotPossibleAdmin)