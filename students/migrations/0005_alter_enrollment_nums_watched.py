# Generated by Django 4.2.4 on 2023-09-09 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_enrollment_nums_watched'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='nums_watched',
            field=models.JSONField(default={'video_video.id': 'nums_of_visit_to_video'}, help_text='Dictionary of times of watching on each video', verbose_name='Times Watched'),
        ),
    ]
