# Generated by Django 4.0.1 on 2022-01-31 14:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('satom', '0003_alter_challenge_completed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challenge',
            name='completed',
        ),
    ]
