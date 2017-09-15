# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-13 05:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0007_workout_member'),
    ]

    operations = [
        migrations.CreateModel(
            name='Max',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Exercise_Name', models.CharField(default='', max_length=200)),
                ('Weight', models.IntegerField(default=0)),
                ('Updated', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='member',
            name='Squat',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='max',
            name='Member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Maxes', to='Users.Member'),
        ),
    ]
