# Generated by Django 4.0.1 on 2022-01-31 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_profile_time_profile_tries'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='challenges',
            field=models.JSONField(default=0),
            preserve_default=False,
        ),
    ]
