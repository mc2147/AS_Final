# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-17 08:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0023_auto_20170917_0828'),
    ]

    operations = [
        migrations.AddField(
            model_name='subworkout',
            name='Alloy_Weight',
            field=models.IntegerField(default=0),
        ),
    ]
