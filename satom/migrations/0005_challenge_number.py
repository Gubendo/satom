# Generated by Django 4.0.1 on 2022-03-02 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('satom', '0004_remove_challenge_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='number',
            field=models.IntegerField(default=0),
        ),
    ]
