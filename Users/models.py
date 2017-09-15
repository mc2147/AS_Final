# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import datetime
from django.contrib.auth.models import User, Group

class Video(models.Model):
	Tags = models.CharField(default = "", max_length=300)
	Title = models.CharField(default = "", max_length=200)
	File = models.FileField(upload_to='static/videos/', max_length=100)
	Thumbnail = models.FileField(upload_to='static/videos/Thumbnails', max_length=100)
	Exercise_Type = models.CharField(default="", max_length=200)
	Description = models.CharField(default="", max_length=1000)
	# Image = models.ImageField(upload_to='static/videos/Thumbnails', max_length=100)

class Member(models.Model):
	User = models.OneToOneField(User)
	Level = models.IntegerField(default=1)
	Squat = models.IntegerField(default=0)
	# Password
	
class Max(models.Model):
	Member = models.ForeignKey(Member, related_name="Maxes")
	Exercise_Name = models.CharField(default="", max_length=200)
	Weight = models.IntegerField(default=0)
	Updated = models.BooleanField(default=False)
	Alloy_Reps = models.IntegerField(default=0)
	Level_Up = models.BooleanField(default=False)
	# Email

# Specific exercise as in 'All Levels'
class Exercise(models.Model):
	# ID = models.CharField(default="", max_length=20)
	Video = models.ForeignKey(Video, blank=True, null=True, related_name="exercises")
	Video_Description = models.CharField(default="", max_length = 1000)
	New_Code = models.CharField(default="", max_length=20)
	Code = models.CharField(default="", max_length=20)
	Name = models.CharField(default="", max_length=200)
	Type = models.CharField(default="", max_length=200)
	Level = models.IntegerField(default=0)
	Bodyweight = models.BooleanField(default=False)


class Set(models.Model):
	Sets = models.IntegerField(default=0)
	Code = models.CharField(default="", max_length=2) # Level + Exercise Type
	Exercise = models.OneToOneField(Exercise, default="", null=True, blank=True)
	Exercise_Type = models.CharField(default="", max_length=200)
	Level = models.IntegerField(default=0)
	Reps = models.IntegerField(default=0)
	Rest_Time = models.DurationField(default=datetime.timedelta(minutes=2, seconds=0))
	Order = models.IntegerField(default=0)

# Row in each table in 'Program'
class SubWorkout(models.Model):
	# Workout = models.OneToOneField(Workout, default="")
	# Exercise = models.OneToOneField(Exercise, default="", null=True, blank=True)
	Exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, blank=True, null=True)
	Exercise_Type = models.CharField(default="", max_length=200)
	Sets = models.IntegerField(default=0)
	Reps = models.IntegerField(default=0)
	Order = models.IntegerField(default=0)
	RPE = models.CharField(default="", max_length=3)
	Deload = models.IntegerField(default=0)
	Money = models.IntegerField(default=0)
	Alloy = models.BooleanField(default=False)
	Alloy_Reps = models.IntegerField(default=0)
	Set_Stats = models.CharField(default=",,/,,/,,/,,", max_length=300)
	Set_1 = models.CharField(default="", max_length=20)
	Set_2 = models.CharField(default="", max_length=20)
	Set_3 = models.CharField(default="", max_length=20)
	Set_4 = models.CharField(default="", max_length=20)
	# Alloy = models.BooleanField(default=False)
	# Alloy_Reps = models.IntegerField(default=0)
class SubWorkout_Template(models.Model):
	Exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, blank=True, null=True)
	Exercise_Type = models.CharField(default="", max_length=200)
	Sets = models.IntegerField(default=0)
	Reps = models.IntegerField(default=0)
	Order = models.IntegerField(default=0)
	RPE = models.CharField(default="", max_length=3)
	Deload = models.IntegerField(default=0)
	Money = models.IntegerField(default=0)

class Workout_Template(models.Model):
	Level_Group = models.IntegerField(default=0)
	Level = models.IntegerField(default=0)
	Ordered_ID = models.IntegerField(default=0)
	Week = models.IntegerField(default=0)
	Day = models.IntegerField(default=0)
	SubWorkouts = models.ManyToManyField(SubWorkout, default="")
	_Date = models.CharField(default="", max_length=10)
	Block_Num = models.IntegerField(default=0)
	Block = models.CharField(default="", max_length=200)
	Alloy = models.BooleanField(default=False)

class Workout(models.Model):
	Alloy = models.BooleanField(default=False)
	Last_Alloy = models.BooleanField(default=False)
	Last_Workout = models.BooleanField(default=False)
	Member = models.ForeignKey(Member, related_name="workouts")
	Submitted = models.BooleanField(default=False)
	Template = models.ForeignKey(Workout_Template)
	Level = models.IntegerField(default=0)
	Ordered_ID = models.IntegerField(default=0)
	Week = models.IntegerField(default=0)
	Day = models.IntegerField(default=0)
	Sets = models.ManyToManyField(Set, default="", null=True, blank=True)
	Date = models.DateField(auto_now=True)
	_Date = models.CharField(default="", max_length=10)
	SubWorkouts = models.ManyToManyField(SubWorkout, default="")
	# _User = models.OneToOneField(User, null=True)

