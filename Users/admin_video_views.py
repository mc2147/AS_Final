# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import *
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, time, timedelta
from django.contrib.auth import logout, login, authenticate
from django.core.files import File
from .views import Levels, Exercise_Types
import json
import stripe

def Admin_Videos(request):
	context = {}
	context["Video_Display"] = []
	context["Video_Display_Test"] = ["videos/Dashboard_Shot.png", 1]
	context["Exercise_Types"] = ["UB Hor Push", "Hinge", "Squat", "UB Vert Push",  "UB Hor Pull", "UB Vert Pull",  "LB Uni Push", 
	"Ant Chain", "Post Chain",  "Isolation", "Iso 2", "Iso 3", "Iso 4", "RFL Load", "RFD Unload 1", "RFD Unload 2"]
	context["Levels"] = Levels
	context["Level_Display"] = []
	# context[""]
	if "Current_Exercises" not in request.session.keys():
		request.session["Current_Exercises"] = []

	for i in Video.objects.all():
		# i.delete()
		row = []
		_Type = i.Exercise_Type
		_Image_URL = "/" + i.File.url
		_Thumbnail_URL = "/" + i.Thumbnail.url
		row.append(i.Title)
		_Name = i.File.name.replace("static/videos/", "")
		print("File Name: " + i.File.name)
		print("File URL: " + i.File.url)
		_URL = i.File.url.replace("static/", "")
		# row.append(_URL)
		row.append(_URL)
		row.append("videos/Dashboard_Shot.png")
		row.append(i.File.url)
		row.append(_Image_URL)
		row.append(_Thumbnail_URL)
		row.append(_Type)
		Exercise_Names = []
		for x in i.exercises.all():
			Exercise_Names.append(x)
		row.append(Exercise_Names)
		context["Video_Display"].append(row)

	if request.method == "POST":
		Selected_Exercise = request.POST['Exercise']
		print(request.POST['Exercise'])
		request.session["Exercise"] = request.POST['Exercise']
		# return HttpResponseRedirect("/admin-videos")

	if request.POST.get("Clear"):
		for i in Video.objects.all():
			i.delete()
		return HttpResponseRedirect("/admin-videos")

	# if request.POST.get("Level"):
	# 	print("LEVEL SELECTED: " + request.POST['Level'])
	# 	request.session["Level"] = int(request.POST['Level'])

	if "Exercise" in request.session.keys():
		_Type = request.session['Exercise']
		context["Selected_Exercise"] = [_Type]
		# context["Exercise_Types"] = Exercise_Types
		context["Exercise_Types"].remove(_Type)

		print("Selected Exercise: " + request.session['Exercise'])
		_Exercises = Exercise.objects.filter(Type = _Type)
		for n in Levels:
			if Exercise.objects.filter(Type = _Type, Level = n).exists():
				_Exercise = Exercise.objects.get(Type=_Type, Level = n)
				context["Level_Display"].append([str(n) + " (" + _Exercise.Name + ")", _Exercise.Name])
	else:
		context["Level_Display"] = Levels

	# if request.POST.get("Exercise"):
	# 	print("EXERCISE SELECTED: " + request.POST['Exercise'])
	# 	request.session["Exercise"] = request.POST['Exercise']
	# 	return HttpResponseRedirect("/admin-videos")

	# if request.method == "POST":
	# 	print(request.POST['Level'])

	if request.POST.get("AddExercises"):
		print("AddExercises Pressed")
		Add_Exercises = request.POST.getlist("Exercise_List")
		for i in Add_Exercises:
			if i not in request.session["Current_Exercises"]:
				request.session["Current_Exercises"].append(i)
		print("Add Exercises: " + str(Add_Exercises))

	context["Current_Exercises"] = request.session["Current_Exercises"]

	if request.POST.get("VideoUploadSubmit"):
		# cwd = os.getcwd()
		# print(str(request.GET.get("VideoUpload")))
		# _File = request.GET.get("VideoUpload")
		_F = request.FILES['VideoUpload']
		print("_F: " + str(_F.name))
		_File = File(_F)
		print("File: " + str(_File.name))
		_Video = Video(Title="Test")
		_Video.File = _File
		_Video.save()		

		# _File = File(open(request.POST.get("VideoUpload"), 'w+'))	
		# print(_File.name)
		# print("Upload button pressed. File Name: " + _File.name)
		return HttpResponseRedirect("/admin-videos")

	if request.POST.get("AddVideo"):
		_Title = request.POST.get("Title")
		_File = File(request.FILES['VideoUpload'])
		_Thumbnail = File(request.FILES['Thumbnail'])
		_Type = request.POST['Exercise']
		_Tags = request.POST['Tags']

		_Description = request.POST['Description']
		print(_Description)

		print(_Title)
		_Video = Video(Title = _Title, File = _File, Thumbnail = _Thumbnail, Exercise_Type=_Type, Description=_Description, Tags=_Tags)
		Add_Exercises = request.POST.getlist("Exercise_List")
		_Video.save()
		for i in Add_Exercises:
			_Exercise = Exercise.objects.get(Name = i)
			_Exercise.Video = _Video
			_Exercise.save()
		request.session["Uploading_Video_PK"] = _Video.pk

		return HttpResponseRedirect("/admin-videos-2")
	return render(request, "adminvideos.html", context)

def Admin_Videos_2(request):
	context = {}
	_Video = Video.objects.get(pk=request.session["Uploading_Video_PK"])
	_Thumbnail_URL = "/" + _Video.Thumbnail.url
	_Video_URL = "/" + _Video.File.url
	_Title = _Video.Title
	_Exercises = _Video.exercises.all()

	context["Video_Title"] = _Title
	context["Thumbnail_URL"] = _Thumbnail_URL
	context["Video_URL"] = _Video_URL
	context["Assigned_Exercises"] = []

	for i in _Exercises:
		context["Assigned_Exercises"].append([i.Name, i.Video_Description])

	if request.POST.get("UpdateDescriptions"):
		for i in _Exercises:
			if request.POST["Description" + i.Name] != "":
				i.Video_Description = request.POST["Description" + i.Name]
				i.save()
		return HttpResponseRedirect("admin-videos-2")

	# if request.POST.get("Submit_Btn"):
	# 	return HttpResponseRedirect("admin-videos-library")

	return render(request, "adminvideos2.html", context)


def Admin_Videos_Library(request):
	context = {}
	context["Videos"] = []

	for v in Video.objects.all():
		row = []
		_Exercises = v.exercises.all()
		exercises_row = []
		
		for i in _Exercises:
			exercises_row.append([i.Name, i.Video_Description])
			# exercises_row.append(i.Video_Description)

		_Thumbnail_URL = "/" + v.Thumbnail.url
		row.append(_Thumbnail_URL)
		row.append(v.Title)
		row.append(v.pk)
		row.append("Edit" + v.Title + str(v.pk)) #3 is button code
		_Tags = v.Tags.split(',')
		Tags = ""
		for _Tag in _Tags:
			Tags = Tags + " , " + _Tag
		row.append(Tags) #4 is tags
		row.append(exercises_row) #5 is exercises
		context["Videos"].append(row)

	if request.method == 'POST':
		# for key in request.GET:
		# 	print("Request Object: " + request.GET[key])
		Keys = []
		for i in request.POST.keys():
			Keys.append(i)
			# print("Key: " + i)
			# print("Key: " + i)
			# print(type(i))
			# if i is int:
			# 	print("Int Key: " + i)
			# if i is str:
			# 	print("String Key: " + i)
				# print("Request Value: " + request.POST[i])
				# request.session["Video_PK"] = int(i)
		# print(request.GET)
		print("First Key: " + Keys[0])
		print("Second Key: " + Keys[1])
		print("REQUEST RECEIVED: ")
		request.session["Video_PK"] = int(Keys[1])
		return HttpResponseRedirect("/admin-videos-library-edit")
	return render(request, "adminvideoslibrary.html", context)

def Admin_Videos_Edit(request):
	context = {}
	_Video = Video.objects.get(pk=request.session["Video_PK"])
	_Type = _Video.Exercise_Type
	_Exercise_List = Exercise.objects.filter(Type=_Type)
	_Assigned_Exercises = _Video.exercises.all()
	context["Display"] = []
	_Thumbnail_URL = "/" + _Video.Thumbnail.url
	_Video_URL = "/" + _Video.File.url

	context["Display"].append(_Thumbnail_URL) 
	context["Display"].append(_Video.Exercise_Type)
	context["Exercise_Types"] = Exercise_Types
	context["Exercise_List"] = []
	context["Assigned_Exercises"] = []
	context["Video_URL"] = _Video_URL
	context["Description"] = _Video.Description
	context["Tags"] = _Video.Tags.split(",")

	# print("Test")
	# print("PK from Edit: " + str(request.session["Video_PK"]))
	for i in _Exercise_List:
		row = []
		row.append(i.Name)
		row.append(i.Level)
		row.append(i.pk)
		context["Exercise_List"].append(row)
	for i in _Assigned_Exercises:
		row = []
		row.append(i.Name)
		row.append(i.Level)
		row.append(i.pk)
		row.append(i.Video_Description)
		context["Assigned_Exercises"].append(row)

	if request.method == "POST":
		print("POST REQUEST DETECTED")
		if request.POST.get("Edit_Video"):
			print("Edit Video")
			if "VideoUpload" in request.FILES.keys():
				print(request.FILES["VideoUpload"])
			# if request.FILES["VideoUpload"] != None:
				_Video_File = File(request.FILES['VideoUpload'])
				_Video.File = _Video_File
				_Video.save()			
		if request.POST.get("Edit_Thumbnail"):
			print("Edit Thumbnail")
			if "ThumbnailUpload" in request.FILES.keys():
				print(request.FILES["ThumbnailUpload"])
			# if request.FILES["ThumbnailUpload"] != None:
				_Thumbnail_File = File(request.FILES['ThumbnailUpload'])
				_Video.Thumbnail = _Thumbnail_File
				_Video.save() 
		if request.POST.get("Add_Tag"):
			print("Add Tag")
			_Video.Tags = _video.Tags + "," + request.POST["Tag"]
		return HttpResponseRedirect('/admin-videos-library-edit')

	if request.GET.get("RemoveExercises"):
		PKs = request.GET.getlist("Remove_Exercises")
		for i in PKs:
			_Exercise = Exercise.objects.get(pk=i)
			print(_Exercise.Name)
			_Exercise.Video = None
			_Exercise.save()
		for i in _Assigned_Exercises:
			if request.GET.get(str(i.pk) + "_Description"):
				i.Video_Description = request.GET[str(i.pk) + "_Description"]
				i.save()
		if request.GET.get("General_Description"):
			_Video.Description = request.GET["General_Description"]
			_Video.save()
		return HttpResponseRedirect('/admin-videos-library-edit')

	if request.GET.get("AddExercises"):
		print("Test Submit")
		PKs = request.GET.getlist("Assign_Exercises")
		print(PKs)
		for i in PKs:
			print(i)
			_Exercise = Exercise.objects.get(pk=i)
			print(_Exercise.Name)
			_Exercise.Video = _Video
			_Exercise.save()
		return HttpResponseRedirect('/admin-videos-library-edit')

	return render(request, "adminvideosedit.html", context)
