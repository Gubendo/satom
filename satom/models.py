from django.db import models
from django.utils import timezone

class Challenge(models.Model):
    word = models.CharField(max_length=20, unique=True)
    number = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return str(self.number) + "_" + self.word + "_" + str(self.date)

class MotPossible(models.Model):
    mot = models.CharField(max_length=20, unique=True)
    difficulte = models.IntegerField(default=1)
    longueur = models.IntegerField(default=0, editable=False)
    used = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        self.longueur = len(self.mot)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.mot + "_l" + str(self.longueur) + "_d" + str(self.difficulte)