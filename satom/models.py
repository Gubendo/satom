from django.db import models

class Challenge(models.Model):
    word = models.CharField(max_length=20)

    def __str__(self):
        return str(self.pk) + "-" + self.word
