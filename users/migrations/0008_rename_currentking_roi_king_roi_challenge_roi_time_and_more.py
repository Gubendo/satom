# Generated by Django 4.0.1 on 2022-02-21 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('satom', '0004_remove_challenge_completed'),
        ('users', '0007_roi'),
    ]

    operations = [
        migrations.RenameField(
            model_name='roi',
            old_name='currentKing',
            new_name='king',
        ),
        migrations.AddField(
            model_name='roi',
            name='challenge',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, to='satom.challenge'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='roi',
            name='time',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='roi',
            name='tries',
            field=models.IntegerField(default=0),
        ),
    ]
