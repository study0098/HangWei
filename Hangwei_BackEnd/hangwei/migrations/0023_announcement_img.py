# Generated by Django 2.2.1 on 2019-05-07 16:55

from django.db import migrations, models
import hangwei.models


class Migration(migrations.Migration):

    dependencies = [
        ('hangwei', '0022_announcement'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='img',
            field=models.ImageField(blank=True, default=None, upload_to=hangwei.models.rename_announcement_file),
        ),
    ]