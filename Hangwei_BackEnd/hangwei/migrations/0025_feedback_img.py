# Generated by Django 2.2.1 on 2019-05-07 18:27

from django.db import migrations, models
import hangwei.models


class Migration(migrations.Migration):

    dependencies = [
        ('hangwei', '0024_message_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='img',
            field=models.ImageField(blank=True, default=None, upload_to=hangwei.models.rename_feedback_file),
        ),
    ]