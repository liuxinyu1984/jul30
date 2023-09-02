# Generated by Django 4.2.3 on 2023-08-20 22:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import embed_video.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0004_lecture'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmbedVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', embed_video.fields.EmbedVideoField()),
                ('title', models.CharField(help_text='e.g. Week 1 Video', max_length=200, verbose_name='Title of Video')),
                ('upload_at', models.DateTimeField(auto_now_add=True, verbose_name='Upload Time')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Update Time')),
                ('lecture', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.lecture', verbose_name='Lecture')),
                ('uploader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Uploader')),
            ],
        ),
    ]