# Generated by Django 2.2.1 on 2019-05-07 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hangwei', '0021_flow'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('announcement_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(default=None, max_length=256)),
                ('detail', models.CharField(default=None, max_length=256)),
                ('announcer', models.CharField(default=None, max_length=256)),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
