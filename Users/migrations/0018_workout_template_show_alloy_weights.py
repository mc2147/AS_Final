# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-16 13:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0017_exercise_tempo'),
    ]

    operations = [
        migrations.AddField(
            model_name='workout_template',
            name='Show_Alloy_Weights',
            field=models.BooleanField(default=False),
        ),
    ]
