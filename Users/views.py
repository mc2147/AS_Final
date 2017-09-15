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
import json
import stripe


Exercise_Types = ["UB Hor Push", "UB Vert Push",  "UB Hor Pull", "UB Vert Pull",  "Hinge", "Squat", "LB Uni Push", 
"Ant Chain", "Post Chain",  "Isolation", "Iso 2", "Iso 3", "Iso 4", "RFL Load", "RFD Unload 1", "RFD Unload 2"]

Levels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

def User_Profile(request):
	context = {}
	return render(request, "userprofile.html", context)

def Logout(request):
	logout(request)
	return HttpResponseRedirect("/")

def Level_Up(request):
	context = {}
	# New_Level = str(request.session["New_Level"])
	# context["Level_Up_Message"] = "Congratulations, you've reached Level " + New_Level + " !! You can access the new Level ___ videos"
	return render(request, "levelup.html", context)

def User_Page(request): 
	_User = request.user
	_Member = Member.objects.get(User = _User)
	# workout_date_list = Workout.objects.values_list('_Date', flat=True).distinct()
	workout_date_list = Workout.objects.filter(Member=_Member).values_list('_Date', flat=True).distinct()
	context = {}
	final_list = []
	context["Patterns"] = []
	context["Workout_Day"] = [[], []]	
	context["Workout_Day_Time"] = [[], [], []]

	context["Workout_Stats"] = []

	_Date = datetime.now().strftime("%m/%d/%Y")
	print("Today's Date: " + _Date)
	_Maxes = _Member.Maxes.all()
	for i in _Maxes:
		print("Max Model - Exercise: " + i.Exercise_Name + " weight: " + str(i.Weight))

	if "Calendar_Date" in request.session.keys():
		print(request.session["Calendar_Date"])
		_Date = request.session["Calendar_Date"]
	# else:
	# 	request.session["Calendar_Date"] = datetime.now().strftime("%m/%d/%Y")

	_Workout = Workout.objects.filter(_Date=_Date, Member=_Member)

	if Workout.objects.filter(_Date=_Date, Member=_Member).exists():
		_Workout = Workout.objects.filter(_Date=_Date, Member=_Member)

		context["Workout_Stats"].append(_Workout[0].Level)
		context["Workout_Stats"].append(_Workout[0].Template.Week)
		context["Workout_Stats"].append(_Workout[0].Template.Day)

		print("Workout(s): " + str(_Workout))
		print(len(_Workout))
		print(_Workout[0])
		print(_Workout[0].SubWorkouts.all())
		print("Workout Date: " + _Workout[0]._Date)
		# _Workout = _Workout[0]
		Workout_Date = datetime.strptime(_Workout[0]._Date, "%m/%d/%Y")

		if request.GET.get("Video"):
			print("Video PK: " + request.GET["Video"])
			_PK = int(request.GET["Video"])
			request.session["Video_PK"] = _PK
			return HttpResponseRedirect("/videos")

		if request.GET.get("Submit_Workout"):
			print(request.GET.keys())
			# if Workout.Last_Workout:
			# 	print("Last Workout")
			# 	Squat_Max = Max.objects.filter(Exercise_Name = "Squat", Member = _Member)
			# 	Hinge_Max = Max.objects.filter(Exercise_Name = "Hinge", Member = _Member)
			# 	UB_Hor_Push_Max = Max.objects.filter(Exercise_Name = "UB Hor Push", Member = _Member)
			# 	# if Squat_Max.Level_Up and Hinge_Max.Level_Up and UB_Hor_Push_Max.Level_Up:
			# 	# 	_Member.Level += 1
			# 	# 	_Member.save()
			# 	request.session["New_Level"] = _Member.Level
			# 		# return HttpResponseRedirect("/level-up")
			# 	# else:
			# 	# _Maxes = _Member.Maxes.all()
			# 		# return HttpResponseRedirect("/level-failed")				
			# 	return HttpResponseRedirect("/level-up")

			for i in _Workout[0].SubWorkouts.all():
				Set_Stats = ""
				if i.Alloy:
					print("Alloy Set!")
					for n in range(i.Sets):
						_Set = ""
						Weight_Code = i.Exercise_Type + "Set" + str(n) + "_Weight"
						RPE_Code = i.Exercise_Type + "Set" + str(n) + "_RPE" 
						Tempo_Code = i.Exercise_Type + "Set" + str(n) + "_Tempo"
						Rep_Code = i.Exercise_Type + "Set" + str(n) + "_Reps"
						if n == i.Sets - 1 and request.GET[Rep_Code] != "":
							Weight_Code = Rep_Code
							if int(request.GET[Rep_Code]) >= i.Alloy_Reps:
								_Max = Max.objects.filter(Exercise_Name = i.Exercise_Type, Member=_Member)
								print("Max Exists: " + str(_Max.exists()))

								if _Max.exists():
									_Max = Max.objects.get(Exercise_Name = i.Exercise_Type, Member=_Member)
									_Max.Level_Up = True
									if _Max.Updated == False:
										# _Max.Weight = int(request.GET[Weight_Code])
										_Max.Updated = True
									_Max.save()
								else:
									New_Max = Max(Exercise_Name = i.Exercise_Type, Member=_Member)
									New_Max.Level_Up = True
									New_Max.save()
								_Set = request.GET[Rep_Code] + ","
								Set_Stats = Set_Stats + "/" + _Set
								i.Set_Stats = Set_Stats
								i.save()
					# 	elif request.GET[Weight_Code] != "":
					# 		print(Weight_Code + ": " + request.GET[Weight_Code])
					# 		print(RPE_Code + ": " + request.GET[RPE_Code])
					# 		print(Tempo_Code + ": " + request.GET[Tempo_Code])
					# 		_Max = Max.objects.filter(Exercise_Name = i.Exercise_Type, Member=_Member)
					# 		print("Max Exists: " + str(_Max.exists()))
					# 		if _Max.exists():
					# 			if _Max.Updated == False:
					# 				_Max.Weight = int(request.GET[Weight_Code])
					# 				_Max.Updated = True
					# 				_Max.save()
					# 		else:
					# 			New_Max = Max(Exercise_Name = i.Exercise_Type, Member=_Member, Weight = request.GET[Weight_Code])
					# 			New_Max.save()

					# 	_Set = _Set + request.GET[Weight_Code] + "," + request.GET[RPE_Code] + "," + request.GET[Tempo_Code]
					# 	Set_Stats = Set_Stats + "/" + _Set
					# i.Set_Stats = Set_Stats
					# i.save()

				else:
					for n in range(i.Sets):
						_Set = ""
						Weight_Code = i.Exercise_Type + "Set" + str(n) + "_Weight"
						RPE_Code = i.Exercise_Type + "Set" + str(n) + "_RPE" 
						Tempo_Code = i.Exercise_Type + "Set" + str(n) + "_Tempo"
						if request.GET[Weight_Code] != "":
							print(Weight_Code + ": " + request.GET[Weight_Code])
							print(RPE_Code + ": " + request.GET[RPE_Code])
							print(Tempo_Code + ": " + request.GET[Tempo_Code])
							_Max = Max.objects.filter(Exercise_Name = i.Exercise_Type, Member=_Member)
							print("Max Exists: " + str(_Max.exists()))
							if _Max.exists():
								if _Max.Updated == False:
									_Max.Weight = int(request.GET[Weight_Code])
									_Max.Updated = True
									_Max.save()
							else:
								New_Max = Max(Exercise_Name = i.Exercise_Type, Member=_Member, Weight = request.GET[Weight_Code])
								New_Max.save()
							# i.
							# _Max_Check = User.Maxes.objects.get(Exercise_Name = i.Exercise_Type)
							# if User.Maxes.objects
							# n.Workouteight = int(Weight_Code)
							# i.Sets = int(Weight_Code)
							# i.Weight = int(Weight_Code)
						_Set = _Set + request.GET[Weight_Code] + "," + request.GET[RPE_Code] + "," + request.GET[Tempo_Code]
						Set_Stats = Set_Stats + "/" + _Set
						# if i.Alloy:
							# if (Reps > i.Alloy_Reps):
							# 
						# Pass = True
						# if i.Level_Up
							# for i in Workout.objects.filter(Level = level, Alloy = True).all():
							# 	if i.Pass == False:
							# 		Pass = False
						# if (Pass)
						# User.Level += 1
						# User.save()
						# return HttpResponseRedirect("/level-up")
					i.Set_Stats = Set_Stats
					i.save()
			_Workout[0].Submitted = True
			_Workout[0].save()			
			return HttpResponseRedirect("/userpage")

		print(str(Workout_Date.strftime("%y/%m/%d")))
		print(str(datetime.now().strftime("%y/%m/%d")))			

			# if (_Workout[0].Alloy):
				# if (_Workout[0].Alloy):

		Same_Day = False
		Past = False
		Future = False

		if Workout_Date.strftime("%y/%m/%d") >= datetime.now().strftime("%y/%m/%d"):
			print("Same Date")
			context["Workout_Day_Time"][1].append("True")
			Same_Day = True
		elif Workout_Date < datetime.now():
			context["Workout_Day_Time"][0].append("True")
			Past = True
		elif Workout_Date > datetime.now():
			Future = True
		# Same_Day = True
		for i in _Workout[0].SubWorkouts.all():
			print("Subworkout: " + i.Exercise_Type + " Sets: " + str(i.Sets))
			row = []
			row.append(i.Exercise_Type)
			row.append(i.Sets)
			row.append(i.Reps)
			row.append(i.RPE)
			row.append(i.Exercise.Name)
			row.append("40-45 lbs")

			sets = []
			sets = [[], [], [], []]
			alloy_sets = [[], [], [], []]
			if i.Money != 0:
				print("Alloy Set Detected: " + str(i.Money))
				i.Alloy = True
				i.save()
			# 	if Past:
			# 		for x in range(i.Sets):
			# 			sets[0].append("Set" + str(x))
			# 	elif Same_Day:
			# 		for x in range(i.Sets):
			# 			sets[1].append(i.Exercise_Type + "Set" + str(x))
			# 	elif Future:
			# 		for x in range(i.Sets):
			# 			sets[1].append(i.Exercise_Type + "Set" + str(x))
			# else:
			if i.Alloy:
				for x in range(i.Sets):
					if x == i.Sets - 1:
						sets[3].append(i.Exercise_Type + "Set" + str(x))
					else:
						sets[0].append("Set" + str(x))
			else:
				if Past:
					for x in range(i.Sets):
						sets[0].append("Set" + str(x))
				elif Same_Day:
					for x in range(i.Sets):
						sets[1].append(i.Exercise_Type + "Set" + str(x))
				elif Future:
					for x in range(i.Sets):
						sets[1].append(i.Exercise_Type + "Set" + str(x))
			Empty_Sets = 4 - i.Sets

			if Empty_Sets > 0:
				for n in range(Empty_Sets):
					sets[2].append("Empty Set")

			# if Workout_Date < datetime.now():
			# 	for i in range(i.Sets):
			# 		sets.append("Set" + str(i))
			# else:
			# 	for i in range(i.Sets):
			# 		sets.append("Set" + str(i))
			row.append(sets)
			row.append(alloy_sets)
			# weight has to come in here too
			if (i.Exercise.Video != None):
				_PK = i.Exercise.Video.pk
				# _Video_URL = "/" + i.Exercise.Video.File.url
				row.append([_PK])
			else:
				row.append([])
			context["Patterns"].append(row)
			# context["Patterns"].append(i.Exercise_Type)
		if len(_Workout[0].SubWorkouts.all()) > 0:
			context["Workout_Day"][0].append("True")
	else:
		context["Workout_Day"][1].append("False")

	Empty_Rows = 5 - len(context["Patterns"])
	# print(Empty_Rows)
	# print(len(context["Patterns"]))
	for x in range(Empty_Rows):
		print(x)

	Split_Date = _Date.split("/")
	context["Curr_Year"] = Split_Date[2]
	context["Curr_Month"] = Split_Date[0]
	context["Curr_Day"] = Split_Date[1]


	for workout_date in workout_date_list:
		parsed_date_list = workout_date.split('/')
		parsed_date_dict = {}
		if (len(parsed_date_list) == 3): 
			parsed_date_dict[str('month')] = str(parsed_date_list[0])
			parsed_date_dict[str('day')] = str(parsed_date_list[1])
			parsed_date_dict[str('year')] = str(parsed_date_list[2])
			final_list.append(parsed_date_dict)

	context['final_list'] = json.dumps(final_list)
	context["Date"] = _Date

	if request.method == "POST":
		return HttpResponseRedirect("/userpage")

	return render(request, "userpage.html", context)

@csrf_exempt 
def Workout_Update(request): 
	context = {}
	context["Date"] = ""
	_User = request.user
	_Member = Member.objects.get(User = _User)
	if request.method == 'POST': 
		if 'TempDate' in request.POST: 
			# test_var = date 
			context["Date"] = request.POST["TempDate"]
			request.session["Calendar_Date"] = request.POST["TempDate"]
			test_var = request.POST['TempDate']
			# print "Request is", request 
			# print test_var
			# print isinstance(test_var, basestring)
			workoutDict = {}
			# need to filter on user id here
			workout_list = Workout.objects.filter(_Date=test_var, Member=_Member)
			counter = 0 
			for workout in workout_list: 
				counter +=1 
				subworkout_list = workout.SubWorkouts.all()
				subworkout_counter = 0 
				 
				for subworkout in subworkout_list: 
					subworkoutDict = {
						'level': str(workout.Level), # for now, extract levels for each subworkout
						'exercise_type': subworkout.Exercise_Type,
						'exercise_name': subworkout.Exercise.Name,
						'sets': str(subworkout.Sets),
						'reps': str(subworkout.Reps),
						'rpe': str(subworkout.RPE),
						'date': workout._Date
					}
					workoutDict[subworkout_counter] = subworkoutDict
					subworkout_counter += 1
			# print workoutDict	
			return HttpResponseRedirect("/userpage")
			# return JsonResponse(workoutDict)
		else: 
			return HttpResponseRedirect("/userpage")
			# return JsonResponse({'status': 'fail'})	
	# if request.method == "POST":
	# 	# print(request.POST["TempDate"])
	# 	context["Date"] = request.POST["TempDate"]
	# 	request.session["Calendar_Date"] = request.POST["TempDate"]

	# return render(request, "userpage.html", context)

@csrf_exempt 
def RPE_Update(request): 
	if request.method == 'POST': 
		current_date = request.POST['current_date']
		# need to filter on user id here
		workout_list = Workout.objects.filter(_Date=current_date);

		for workout in workout_list: 
				subworkout_list = workout.SubWorkouts.all()
				subworkout_counter = 0 
				 
				for subworkout in subworkout_list: 
					if (subworkout_counter == 0): 
						subworkout.RPE = request.POST['RPE_row1']
						subworkout.save()
						workout.save()
					elif (subworkout_counter == 1): 
						subworkout.RPE = request.POST['RPE_row2']
						subworkout.save()
						workout.save()
					elif (subworkout_counter == 2): 
						subworkout.RPE = request.POST['RPE_row3']
						subworkout.save()
						workout.save()
					elif (subworkout_counter == 3): 
						subworkout.RPE = request.POST['RPE_row4']
						subworkout.save()
						workout.save()
					elif (subworkout_counter == 4): 
						subworkout.RPE = request.POST['RPE_row5']
						subworkout.save()
						workout.save()
					
					# subworkoutDict = {
					# 	'level': str(workout.Level),
					# 	'exercise_type': subworkout.Exercise_Type,
					# 	'exercise_name': subworkout.Exercise.Name,
					# 	'sets': str(subworkout.Sets),
					# 	'reps': str(subworkout.Reps),
					# 	'date': workout._Date
					# }
					# workoutDict[subworkout_counter] = subworkoutDict
					subworkout_counter += 1

		return HttpResponse('success'); 


Level_Names = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6", "Level 7", "Level 8", "Level 9", "Level 10", "Level 11", "Level 12", "Level 13", "Level 14", "Level 15",
"Level 16", "Level 17", "Level 18", "Level 19", "Level 20", "Level 21", "Level 22", "Level 23", "Level 24", "Level 25"]

def Past_Workouts(request):
	context = {}
	_User = request.user
	_Member = Member.objects.get(User=_User)
	Workouts = _Member.workouts.all()
	
	context["Workout_Info"] = []
	context["Selected_Workout"]  = []
	context["Workout_Date"] = [[], []]

	if "Selected_Date" in request.session.keys():
		_Date = request.session["Selected_Date"]
		context["Workout_Date"] = [_Date]
		_Workout = Workout.objects.get(_Date = _Date, Member = _Member)
		context["Workout_Level"] = _Workout.Level
		for n in _Workout.SubWorkouts.all():
			Sub = []
			Sub.append(n.Exercise_Type)
			Sub.append(n.Exercise.Name)
			Sub.append(n.Sets)
			Stats = n.Set_Stats.split("/")
			Stat_List = [[], []]
			for string in Stats:
				if n.Alloy and string == Stats[-1]:
					# Set_List = string.split(",")
					Set_List = "145,Alloy,8".split(",")
					Stat_List[1].append(Set_List)
				else:
					Set_List = "145,8,8".split(",")
					# Set_List = string.split(",")
					Stat_List[0].append(Set_List)
			Sub.append(Stat_List)
			context["Selected_Workout"].append(Sub)
			Sub.append(n.Set_Stats)
	for i in Workouts:
		row = []
		row.append(i._Date)
		row.append(i.Level)
		row.append(i.Template.Week)
		row.append(i.Template.Day)
		if i.Alloy:
			row.append("Alloy")
		else:
			row.append("Regular")
		context["Workout_Info"].append(row)

	if request.method == "POST":
		print(request.POST["Submitted_Date"])
		request.session["Selected_Date"] = request.POST["Submitted_Date"]
		return HttpResponseRedirect("/past-workouts")
	return render(request, "pastworkouts.html", context)

def Videos(request): 
	# _User = request.user
	# _Member = Member.objects.get(User = _User)
	# _Level = Member.Level
	context = {}
	context["Videos"] = []
	context["Levels"] = Levels

	context["Current_Level"] = []

	context["Display_Levels"] = Level_Names

	context["Video_Group_1"] = []
	context["Video_Group_2"] = []
	context["Video_Group_3"] = []
	context["Video_Group_4"] = []
	context["Video_Group_5"] = []

	_Exercises = Exercise.objects.all()
	_Videos = Video.objects.all()

	# if 'Current_Level' in request.session.keys():
	# 	context["Current_Level"] = [request.session["Current_Level"]]

	for i in _Exercises:
		if i.Level <= 5:
			context["Video_Group_1"].append(i.Name)
		elif i.Level <= 10:
			context["Video_Group_2"].append(i.Name)
		elif i.Level <= 15:
			context["Video_Group_3"].append(i.Name)
		elif i.Level <= 20:
			context["Video_Group_4"].append(i.Name)
		elif i.Level <= 25:
			context["Video_Group_5"].append(i.Name)
		if request.GET.get(str(i.pk)):
			print("PK Submitted: " + str(i.pk) + " " + i.Name)

	context["Video_URL"] = ""

	if "Video_PK" in request.session.keys():
		Selected_Video = Video.objects.get(pk=request.session["Video_PK"])
		context["Video_URL"] = "/" + Selected_Video.File.url
		context["Video_Title"] = Selected_Video.Title

	for i in _Videos:
		row = []
		_Name = i.Title
		_Thumbnail_URL = "/" + i.Thumbnail.url
		row.append(_Name)
		row.append(i.pk)
		row.append(_Thumbnail_URL)
		context["Videos"].append(row)


	for i in _Videos:
		if request.GET.get(str(i.pk)):
			print("Video PK Submitted: " + str(i.pk) + " " + i.Title)
			request.session["Video_PK"] = i.pk
			context["Video_URL"] = "/" + i.File.url
			context["Video_Title"] = i.Title
			return HttpResponseRedirect("/videos")
			# return render(request, "videos.html", context)



	# if request.method == "GET":
		# print("Form Submitted")
		# print("Video PK: " + str(request.GET.get("Video_PK")))
	if request.method == "POST":
		print("POST DETECTED")
	if request.GET.get("search_submit"):
		context["Videos"] = []
		_Search_Entry = request.GET.get("search")
		_Search_Terms = _Search_Entry.split()
		_Level_String = request.GET.get("Level")
		# print(_Level_String)
		if (_Level_String != "All Levels"):
			_Level_Split = _Level_String.split()
			_Level = int(_Level_Split[1])
		request.session['Current_Level'] = _Level_String
		context["Current_Level"] = [_Level_String]
		Last_Levels = []
		context["Display_Levels"] = Level_Names	

		# context["Display_Levels"].remove(_Level_String)		
		# if _Level != 0:
			# for i in context["Display_Levels"]:
			# 	if i != _Level_String:
			# 		Last_Levels.append(i)
			# context["Display_Levels"] = []
			# context["Display_Levels"].append(_Level_String)
			# context["Display_Levels"] = context["Display_Levels"] + Last_Levels
		# print("Searching:")
		# print(_Search_Entry)
		# print(_Search_Terms)
		# print(_Level)
		if (_Level_String == "All Levels"):
			context["Display_Levels"] = ["All Levels"] + Level_Names
			print("All Levels Selected")
		if (_Level_String != "All Levels" and _Level != 0):
			_Level_Num = int(_Level)
			_Exercises = Exercise.objects.filter(Level = _Level_Num)
			context["Display_Levels"] = [_Level_String] + Level_Names

		if _Search_Entry == "":
			for i in _Videos:
				row = []
				_Name = i.Title
				_Thumbnail_URL = "/" + i.Thumbnail.url
				row.append(_Name)
				row.append(i.pk)
				row.append(_Thumbnail_URL)
				context["Videos"].append(row)
			# for i in _Exercises:
			# 	_Name = i.Name
			# 	row = []
			# 	row.append(_Name)
			# 	row.append(i.pk)
			# 	context["Videos"].append(row)
			return render(request, "videos.html", context)
		else:
			print("Line 148 Executing")
			for i in _Videos:
				_Tag_List = i.Tags.split(',')
				_Tags = ""
				for t in _Tag_List:
					_Tags = _Tags + t + " "
				_Title = i.Title
				_Check_Against = _Tags + " " + _Title
				_Thumbnail_URL = "/" + i.Thumbnail.url

				for _Term in _Search_Terms:
					if _Term in _Check_Against:
						# context["Videos"].append(_Title)
						context["Videos"].append([_Title, i.pk, _Thumbnail_URL])
					elif _Term.capitalize() in _Check_Against:
						# context["Videos"].append(_Title)
						context["Videos"].append([_Title, i.pk, _Thumbnail_URL])
					elif _Term.lower() in _Check_Against:
						# context["Videos"].append(_Title)
						context["Videos"].append([_Title, i.pk, _Thumbnail_URL])
			# for i in _Exercises:
			# 	_Name = i.Name				
			# 	for _Term in _Search_Terms:
					# print(_Term)
					# print(_Term.lower())
					# print(_Term.capitalize())
					# if _Term in _Name:
					# 	context["Videos"].append(_Name)
					# elif _Term.capitalize() in _Name:
					# 	context["Videos"].append(_Name)
					# elif _Term.lower() in _Name: 
					# 	context["Videos"].append(_Name)
			return render(request, "videos.html", context)
	return render(request, "videos.html", context)

Days_Of_Week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def Member_Home(request):
	context = {}
	context["Sets"] = []
	context["Test"] = "Test context"
	anonymous = True
	user = request.user
	if (user.is_anonymous() == False): 
		Current_Workout = Workout.objects.get(_User = user, Date=datetime.date.today())
		anonymous = False
	count = 0
	if (anonymous == False):
		for i in Current_Workout.Sets.all():
			if i.Order == count + 1:
				row = []
				row.append(i.Exercise)
				row.append(i.Reps)
				row.append(i.Rest_Time)
				count += 1
				Context["Sets"].append(row)

	if(request.GET.get("form_test")):
		print("test form")
		return HttpResponseRedirect('/member-home/')

	if(request.GET.get("test_button")):
		print("test button")
		context["Test"] = "Test change"
		return render(request, "member_home.html", context)
	# new_user = User.objects.create(username=email, first_name=f_name, last_name=l_name, password=p_1)
	 # new_user.save()
	return render(request, "member_home.html", context)


