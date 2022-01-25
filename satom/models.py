from django.db import models
from django.contrib.auth.models import User

class Challenge(models.Model):
    word = models.CharField(max_length=20)
    completed = models.ManyToManyField(User)

    def __str__(self):
        return str(self.pk) + "-" + self.word
