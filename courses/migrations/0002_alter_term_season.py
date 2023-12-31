# Generated by Django 4.2.3 on 2023-08-11 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='term',
            name='season',
            field=models.CharField(choices=[('Fall', 'Fall'), ('Spring', 'Spring'), ('Summer_1', 'Summer_1'), ('Summer_2', 'Summer_2')], help_text='Season of the term, e.g. Fall.', max_length=8, verbose_name='Season'),
        ),
    ]
