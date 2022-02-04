# Generated by Django 4.0.1 on 2022-01-31 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('satom', '0004_remove_challenge_completed'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='bio',
        ),
        migrations.AddField(
            model_name='profile',
            name='completedChall',
            field=models.ManyToManyField(to='satom.Challenge'),
        ),
    ]