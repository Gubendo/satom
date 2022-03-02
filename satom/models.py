from django.db import models

class Challenge(models.Model):
    word = models.CharField(max_length=20)
    number = models.IntegerField(default=0)

    def __str__(self):
        return str(self.number) + "-" + self.word + str(self.pk)
