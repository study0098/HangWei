# Generated by Django 2.1.2 on 2019-04-13 02:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hangwei', '0011_window_img'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='comment', to='hangwei.Comment')),
                ('reply_new', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='reply_new', to='hangwei.CommentReply')),
                ('reply_old', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='reply_old', to='hangwei.CommentReply')),
                ('user_new', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='user_new', to='hangwei.User')),
                ('user_old', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='user_old', to='hangwei.User')),
            ],
        ),
    ]
