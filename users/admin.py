from django.contrib import admin
from users.models import Profile, Roi

class ProfileAdmin(admin.ModelAdmin):
    pass

class RoiAdmin(admin.ModelAdmin):
    pass

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Roi, RoiAdmin)
