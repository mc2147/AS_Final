# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-17 11:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0024_subworkout_alloy_weight'),
    ]

    operations = [
        migrations.AddField(
            model_name='stat',
            name='Alloy_Performance_Reps',
            field=models.IntegerField(default=0),
        ),
    ]