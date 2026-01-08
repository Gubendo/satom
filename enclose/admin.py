from django.contrib import admin
from .models import PuzzleScore, EnclosePuzzle

@admin.register(PuzzleScore)
class PuzzleScoreAdmin(admin.ModelAdmin):
    list_display = ("user", "puzzle_id", "area", "created_at")
    actions = ["reset_score"]

    def reset_score(self, request, queryset):
        queryset.delete()

class EnclosePuzzleAdmin(admin.ModelAdmin):
    pass

admin.site.register(EnclosePuzzle, EnclosePuzzleAdmin)