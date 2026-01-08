from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

class EnclosePuzzle(models.Model):
    puzzle_id = models.CharField(max_length=32, unique=True)
    date = models.DateField(unique=True)
    size = models.PositiveIntegerField()
    max_walls = models.PositiveIntegerField()
    
    grid = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.puzzle_id

class PuzzleScore(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enclose_scores"
    )
    puzzle = models.ForeignKey(
        EnclosePuzzle,
        on_delete=models.CASCADE,
        related_name="scores"
    )

    area = models.PositiveIntegerField()
    walls_used = models.PositiveIntegerField()
    walls = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "puzzle")
        ordering = ["-area", "walls_used","created_at"]

    def __str__(self):
        return f"{self.user} – {self.puzzle} ({self.area})"