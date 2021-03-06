# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-11 12:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0003_auto_20170818_2136'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubWorkout_Template',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Exercise_Type', models.CharField(default='', max_length=200)),
                ('Sets', models.IntegerField(default=0)),
                ('Reps', models.IntegerField(default=0)),
                ('Order', models.IntegerField(default=0)),
                ('RPE', models.CharField(default='', max_length=3)),
                ('Deload', models.IntegerField(default=0)),
                ('Money', models.IntegerField(default=0)),
                ('Exercise', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Users.Exercise')),
            ],
        ),
        migrations.AddField(
            model_name='subworkout',
            name='Set_1',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='subworkout',
            name='Set_2',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='subworkout',
            name='Set_3',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='subworkout',
            name='Set_4',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='subworkout',
            name='Set_Stats',
            field=models.CharField(default='', max_length=300),
        ),
        migrations.AddField(
            model_name='workout',
            name='Submitted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='member',
            name='Level',
            field=models.IntegerField(default=1),
        ),
    ]
