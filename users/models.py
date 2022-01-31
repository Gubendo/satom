from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from satom.models import Challenge

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    completedChall = models.ManyToManyField(Challenge)
    challenges = models.JSONField(default=list)

    def __str__(self):
        return str(self.user)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
