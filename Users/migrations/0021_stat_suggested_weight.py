# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-16 17:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0020_auto_20170916_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='stat',
            name='Suggested_Weight',
            field=models.IntegerField(default=0),
        ),
    ]