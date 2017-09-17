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
from sign_up_views import Get_Weight, Get_Max

Exercise_Types = ["UB Hor Push", "UB Vert Push",  "UB Hor Pull", "UB Vert Pull",  "Hinge", "Squat", "LB Uni Push", 
"Ant Chain", "Post Chain",  "Isolation", "Iso 2", "Iso 3", "Iso 4", "RFL Load", "RFD Unload 1", "RFD Unload 2"]

Levels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

# RPEs = ["X (Failure)", "1-2", "3-4", "5-6", "7", "8", "8.5", "9", "9.5", "10"]

RPEs = [["1-2", 1], ["3-4", 3], ["5-6", 5], ["7", 7], ["8", 8], ["8.5", 8.5], ["9", 9], ["9.5", 9.5], ["10", 10]]
RPEs.reverse()

def Contact_And_Support(request): 
	return render(request, "contact.html")

def User_Profile(request):
	context = {}
	_User = request.user
	_Member = Member.objects.get(User=_User)

	_Stats = _Member.Stats.all()
	context["Stats"] = []

	for i in _Stats:
		print("Stat")
		context["Stats"].append([i.Type, i.Exercise_Name, i.Max])
		Related_Exercise = Exercise.objects.get(Level = _Member.Level, Type = i.Type)
		i.Exercise_Name = Related_Exercise.Name
		i.save()
		if i.Type == "":
			i.delete()

	return render(request, "userprofile.html", context)

def Logout(request):
	logout(request)
	return HttpResponseRedirect("/")

def Level_Up(request):
	context = {}
	# New_Level = str(request.session["New_Level"])
	# context["Level_Up_Message"] = "Congratulations, you've reached Level " + New_Level + " !! You can access the new Level ___ videos"
	return render(request, "levelup.html", context)

def Check_Level_Up(_Member):
	Level_Up = False
	Curr_Level = _Member.Level
	
	Stats = _Member.Stats.all()
	
	# Squat, Created = Stat.objects.get_or_create(Member = _Member, Type="Squat")
	# Bench, Created = Stat.objects.get_or_create(Member = _Member, Type="UB Hor Press")
	# Hinge, Created = Stat.objects.get_or_create(Member = _Member, Type="Hinge")
	print("CHECK LEVEL UP FUNCTION:")
	for x in Stats:
		print("Stat Check: " + x.Type + " Passed: " + str(not x.Failed))
	# 	if x.Level < Curr_Level - 2:
	# 		return False
	# 	if x.Failed and x.Core: 
	# 		return False

	# if Squat.Level_Up and Bench.Level_Up and Hinge.Level_Up:
	# 	_Member.Level += 1
	# 	_Member.save()
	# 	for x in Stats:
	# 		x.Reset()
	# 		x.save()
	# 	return True
	# return Level_Up

def Tutorial(request):
	context = {}
	return render(request, "tutorial.html", context)

def User_Page_Alloy(request):
	context = {}
	return render(request, "userpage_alloy.html", context)

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
	context["Tempo"] = []
	context["Workout_Stats"] = []
	context["Workout_Info"] = ""
	context["Alloy"] = ""
	# Reversed_RPE = reversed(RPEs)
	# RPEs.reverse()
	context["RPE_List"] = RPEs

	_Date = datetime.now().strftime("%m/%d/%Y")
	print("Today's Date: " + _Date)
	_Stats = _Member.Stats.all()
	# for i in _Stats:
	# 	print("Stat - Exercise: " + i.Type + " weight: " + str(i.Max) + " Passed: " + str(not i.Failed))
	# 	if i.Type == "":
	# 		i.delete()
	if "Calendar_Date" in request.session.keys():
		print(request.session["Calendar_Date"])
		_Date = request.session["Calendar_Date"]
	# else:
	# 	request.session["Calendar_Date"] = datetime.now().strftime("%m/%d/%Y")

	Workout_Day = False
	Alloy_Workout = False
	Show_Alloy = False

	Requires_Tempo = False

	if request.GET.get("Level_Up_Check"):
		print("Level Up Check")
		Check_Level_Up(_Member)
	
	if Workout.objects.filter(_Date=_Date, Member=_Member).exists():
		_Workout = Workout.objects.get(_Date=_Date, Member=_Member)
		Workout_Day = True
		context["Workout_Info"] = "Level " + str(_Workout.Level) + ", Week " + str(_Workout.Template.Week) + ", Day " + str(_Workout.Template.Day)
		if _Workout.Template.Alloy:
			Alloy_Workout = True
			if _Workout.Show_Alloy_Weights:
				Show_Alloy = True
			context["Alloy"] = "(Alloy)"
		for _Sub in _Workout.SubWorkouts.all():
			if _Sub.Exercise.Tempo:
				Requires_Tempo = True
		Workout_Date = datetime.strptime(_Workout._Date, "%m/%d/%Y")
		# Level {{Workout_Stats.0}}, Week {{Workout_Stats.1}}, Day {{Workout_Stats.2}}
	else:
		context["Workout_Day"][1].append("Y")
		context["Workout_Info"] = "No Workout For This Day"

	Show_Alloy = False

	if Workout_Day:
		context["Workout_Stats"].append(_Workout.Level)
		context["Workout_Stats"].append(_Workout.Template.Week)
		context["Workout_Stats"].append(_Workout.Template.Day)

		if Requires_Tempo:
			context["Tempo"].append("Yes")

		if Show_Alloy:
			context["Show_Submit"] = ["Show"]
			context["Show_Get_Alloy"] = []
		else:
			context["Show_Submit"] = ["Show"]
			context["Show_Get_Alloy"] = ["Show"]
		# Display Context Function Here

	if request.GET.get("Video"):
		print("Video PK: " + request.GET["Video"])
		_PK = int(request.GET["Video"])
		request.session["Video_PK"] = _PK
		return HttpResponseRedirect("/videos")

	# if request.GET.get("Submit_Workout") or request.GET.get("Get_Alloy"):

	if request.GET.get("clear_all"):
		for i in _Workout.SubWorkouts.all():
			Reset_Sets = []
			for n in range(i.Sets):				
				Reset_Sets.append("B" + str(n + 1) + ",,,,")
			i.Set_Stats = "/".join(Reset_Sets)
			# i.Set_Stats = "/".join(Filled_Sets)
			i.Show_Alloy = False
			i.save()
		return HttpResponseRedirect("/userpage")

	if request.GET.get("Tester"):
		print("TESTER")
		for i in request.GET.keys():
			# if "UB" in 
			print("Request Key: " + i)
			# for _Sub in _Workout.SubWorkouts.all():
		for _Sub in _Workout.SubWorkouts.all():
			_Sub.Show_Alloy = False
			_Sub.save()
		return HttpResponseRedirect("/userpage")

	if Workout_Day:
		_Workout = Workout.objects.get(_Date=_Date, Member=_Member)
		# if Alloy_Workout:

		print("Workout(s): " + str(_Workout))
		# print(len(_Workout))
		print(_Workout)
		print(_Workout.SubWorkouts.all())
		print("Workout Date: " + _Workout._Date)
		# _Workout = _Workout[0]
		Workout_Date = datetime.strptime(_Workout._Date, "%m/%d/%Y")

		Same_Day = False
		Past = False
		Future = False

		Get_Alloy_Pressed = False

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
			# Creating Context Here
		context["Tempo"].append("Y")
		for i in _Workout.SubWorkouts.all():
			# GETTING WEIGHTS FOR FIRST COLUMN
			_Stat, Created = Stat.objects.get_or_create(Type=i.Exercise_Type, Member=_Member)						
			Alloy_Sub = False
			Row = {}
			Row["Money"] = ""

			Set_Loop = i.Sets
			
			Set_List = i.Set_Stats.split("/")
			if "" in Set_List:
				Set_List.remove("")
			Row["Set_Stats"] = str(Set_List)

			Num_Filled_Sets = 0

			Row["Filled_Sets"] = []

			Filled_Sets = []

			Row["Filled_Alloy"] = []

			for Set in Set_List:
				if Set != "":
					if Set[0][0] == "B":
						Row["Set_Stats"] += Set.split(",")[0]
						First_Empty_Set_Num = Set.split(",")[0][1]
						Num_Filled_Sets = int(First_Empty_Set_Num) - 1
						break 
					elif Set[0][0] == "R" or  Set[0][0] == "A":
						Filled_Sets.append(Set)

			# Filled_Sets.remove("A")

			for Set in Filled_Sets:
				# if Set == "A":
				# 	Filled_Sets.remove(Set)
				if Set != "" and Set != "A":
					Index = Filled_Sets.index(Set) 
					Type = Set[0]
					print("Set (line 242): " + str(Set) + " Index: " + str(Index + 1))
					print(Set[1])
					_List = Set.split(",")
					_List[0] = Type + str(Index + 1)
					Set = ",".join(_List)
					print(Set)
					Filled_Sets[Index] = Set
				# Set[1] = str(Index)

			Filled_Set_String = "/".join(Filled_Sets)

			# RESET
			i.Set_Stats = ""
			Reset_Sets = []
			for n in range(i.Sets):				
				Reset_Sets.append("B" + str(n + 1) + ",,,,")
				# Reset_Sets.append("R" + str(n + 1) + ",,,,")

			i.Filled_Sets = len(Filled_Sets)

			# i.Set_Stats = "/".join(Reset_Sets)
			i.Set_Stats = "/".join(Filled_Sets)
			i.save()

			# i.Set_Stats = Filled_Set_String
			# i.save()

			# for Set in Filled_Sets:
			# 	Row["Set_Stats"] += " Filled Set Test: " + str(Set)
			
			# Row["Set_Stats"] += " Filled Set String: " + Filled_Set_String

			Num_Filled_Sets = len(Filled_Sets)


			for n in range(Num_Filled_Sets):
				# Row["Set_Stats"] += " Filled Set Test: " + str(Set)
				# Row["Set_Stats"] += ", Filled Set: " + str(n)
				# Row["Set_Stats"] += str([Set_List[n].split(",")])
				Set_Info = Set_List[n].split(",")
				if Set_Info != "" and len(Set_Info) > 1:
					Filled_Set = {}
					Filled_Set["Reps"] = Set_Info[1]
					Filled_Set["Weight"] = Set_Info[2]  
					Filled_Set["RPE"] = Set_Info[3] 
					Filled_Set["Tempo"] = Set_Info[4] 
					if Set_Info[0] == "A" + str(i.Sets):
						Row["Filled_Alloy"].append(Filled_Set)
					else:
						Row["Filled_Sets"].append(Filled_Set)
					Set_Loop -= 1

			Remaining_Sets = i.Sets - Num_Filled_Sets

			# Row["Set_Stats"] = ""
			if Alloy_Workout and i.Money != 0 and i.Money != None:
				Alloy_Sub = True
				Row["Money"] = i.Money
				_Stat.Alloy_Reps = i.Money
				_Stat.save()
			Test_Dict = {"Test": "Test dict again"}
			Row["Exercise_Type"] = i.Exercise_Type
			Row["Exercise_Name"] = i.Exercise.Name
			Row["Sets"] = i.Sets
			Row["Reps"] = i.Reps
			Row["RPE"] = i.RPE
			Row["Video_PK"] = []
			Row["Input_ID"] = i.Exercise_Type + "_Input"
			if (i.Exercise.Video != None):
				_PK = i.Exercise.Video.pk
				Row["Video_PK"].append(_PK)
			
			Row["Suggested_Weight"] = ""
			if _Stat.Max != 0:
				Range_Min = _Stat.Max - (_Stat.Max % 5)
				Range_Max = Range_Min + 5
				Weight_String = str(Range_Min) + "-" + str(Range_Max) + " lbs" 
				Row["Suggested_Weight"] = Weight_String

			Row["Deload"] = "None"

			if i.Deload != 0 and i.Deload != None:
				Row["Deload"] = i.Deload


			Row["Weight_Col"] = [[], [], []]
			Row["Reps_Col"] = [[], [], []]
			Row["RPE_Col"] = [[], [], []]
			Row["Tempo_Col"] = [[], [], []]
			Row["Same_Day_Col"] = {}

			Row["Same_Day_Col"]["Post_Show"] = {}

			Row["Same_Day_Col"]["Post_Show"]["Regular"] = []
			Row["Same_Day_Col"]["Post_Show"]["Alloy_Sub"] = []
			Row["Same_Day_Col"]["Post_Show"]["Alloy_Set"] = []

			Row["Same_Day_Col"]["Pre_Show"] = {}
			Row["Same_Day_Col"]["Pre_Show"]["Regular"] = []
			Row["Same_Day_Col"]["Pre_Show"]["Alloy_Sub"] = []
			Row["Same_Day_Col"]["Pre_Show"]["Alloy_Set"] = []


			Row["Tempo"] = []
			Row["Changeable"] = {"Yellow": [], "Normal" : []}
			Row["Non_Changeable"] = {"Yellow": [], "Normal" : []}

			Sub_Tempo = False

			if "Tempo" in i.Exercise.Name:
				Sub_Tempo = True
				Row["Tempo"].append("Y")

			Row["Empty_Sets"] = []
			# We need to know:
				# If Alloy
			Set_Scheme = []

			if Alloy_Sub:
				Set_Loop -= 1

			Row["Tempo"].append("Y")

			# Set_List = i.Set_Statsif i.Show_Alloy:


			# if i.Show_Alloy:
			# Show filled stats, then changeable alloy set at the end
			# if not alloy
			# Show regular rows
			# if alloy but not shown yet
			# Show regular rows and unchangeable last one
			# Types of Rows
			# Fixed normal, Fixed highlighted/Get_Alloy Button, Input normal, Input Alloy
			# Fixed, Input -> Alloy, Normal
			# bools: i.Alloy, i.Show_Alloy
			# Order: Fixed normal, Input normal, Fixed alloy, Input alloy
			Row["Alloy_Sets"] = {"Fixed": [], "Input": [], "Completed": []}
			Row["Regular_Sets"] = {"Fixed": [], "Input": []}
			
			Row["Alloy_Weight"] = _Stat.Alloy_Weight - (_Stat.Alloy_Weight % 5) + 5

			print(i.Exercise_Type + " Set Scheme: ")			
			for R in range(Remaining_Sets):
				Set_Row = [i.Exercise_Type + "Set" + str(R), ""]
				Alloy_Row = [i.Exercise_Type + "Alloy_Set", ""]
				if i.Alloy and Alloy_Sub:
					if R == Remaining_Sets - 1:
						if i.Show_Alloy:
							print("Alloy Set (Input)")
							Row["Alloy_Sets"]["Input"].append(Alloy_Row)
						else:
							Row["Alloy_Sets"]["Fixed"].append(Alloy_Row)
							print("Alloy Set (Fixed)")
						continue
					else:
						Row["Regular_Sets"]["Input"].append(Set_Row)
						print("Regular Set (Input)")
				else:
					Row["Regular_Sets"]["Input"].append(Set_Row)
					print("Regular Set (Input)")


			for x in range(Set_Loop):
				Set_Type = [i.Exercise_Type + "Set" + str(x), ""]

				# WEIGHT STRING HERE
				if Show_Alloy:
					if not Alloy_Sub:
						Row["Same_Day_Col"]["Post_Show"]["Regular"].append([i.Exercise_Type + "Set" + str(x), ""])
					else:
						Row["Same_Day_Col"]["Post_Show"]["Alloy_Sub"].append([i.Exercise_Type + "Set" + str(x), ""])						
					Row["Non_Changeable"]["Normal"].append([i.Exercise_Type + "Set" + str(x), Weight_String])					

				else:
					if not Alloy_Sub:
						Row["Same_Day_Col"]["Pre_Show"]["Regular"].append([i.Exercise_Type + "Set" + str(x), ""])
					else:
						Row["Same_Day_Col"]["Pre_Show"]["Alloy_Sub"].append([i.Exercise_Type + "Set" + str(x), ""])						
					Row["Changeable"]["Normal"].append([i.Exercise_Type + "Set" + str(x), Weight_String])					
			
			Last_Set_Index = i.Sets - 1

			if Alloy_Sub:
				if Show_Alloy:
					Weight = _Stat.Alloy_Weight - (_Stat.Alloy_Weight % 5) + 5
					Weight_String = str(Weight) + " lbs"
					Row["Same_Day_Col"]["Post_Show"]["Alloy_Set"].append([i.Exercise_Type + "Set" + str(Last_Set_Index), Weight_String])	
					Row["Changeable"]["Yellow"].append([i.Exercise_Type + "Set" + str(Last_Set_Index), Weight_String])					
				else:
					Row["Same_Day_Col"]["Pre_Show"]["Alloy_Set"].append([i.Exercise_Type + "Set" + str(Last_Set_Index), ""])						
					Row["Non_Changeable"]["Yellow"].append([i.Exercise_Type + "Set" + str(Last_Set_Index), Weight_String])					

			Empty_Sets = 4 - i.Sets

			if Empty_Sets > 0:
				for n in range(Empty_Sets):
					Row["Empty_Sets"].append("Empty_Set")

			context["Patterns"].append(Row)

			if request.GET.get(i.Exercise_Type + "_Get_Alloy"):
				print("Getting Alloy Set for: " + i.Exercise_Type)
				i.Show_Alloy = True
				i.save()
				Get_Alloy_Pressed = True
				request.session["Show_Alloy_Type"] = i.Exercise_Type
				# _Stat.Alloy_Weight = Get_Weight(_Stat.Max, _Reps_Estimate + 1, 10) 
				# return HttpResponseRedirect("/userpage")

		if len(_Workout.SubWorkouts.all()) > 0:
			context["Workout_Day"][0].append("True")
		else:
			context["Workout_Day"][1].append("False")

		Split_Date = _Date.split("/")
		context["Curr_Year"] = Split_Date[2]
		context["Curr_Month"] = Split_Date[0]
		context["Curr_Day"] = Split_Date[1]

		print("ALL STATS: ")
		for stat in Stat.objects.all():
			Type = stat.Type
			if stat.Level_Up and not stat.Failed:
				print(Type + " PASS")
			elif not stat.Level_Up and stat.Failed:
				print(Type + " FAIL")
			# else: 
			# 	print(Type + " " + str(stat.Level_Up) + " " + str(stat.Failed))

		if request.GET.get("Submit_Workout") or request.GET.get("Get_Alloy") or Get_Alloy_Pressed:
			print(request.GET.keys())
			for _Sub in _Workout.SubWorkouts.all():
				Set_Stats = ""
				Alloy_Sub = False
				if Alloy_Workout and _Sub.Money != 0 and _Sub.Money != None:
					Alloy_Sub = True

				_E_Type = _Sub.Exercise_Type
				_E_Name = _Sub.Exercise.Name

				_Stat, Created = Stat.objects.get_or_create(Type=_E_Type, Member=_Member)

				Initial_Sets = _Sub.Sets - _Sub.Filled_Sets

				if request.GET.get("Get_Alloy"):
					Initial_Sets -= 1

				if Alloy_Sub:
					Initial_Sets -= 1

				for n in range(Initial_Sets):
					_Reps = str(_Sub.Reps)
					_Weight = ""
					_RPE = "10"
					_Tempo = ""

					Prefix = _E_Type + "Set" + str(n)

					Rep_Code = Prefix + "_Reps"
					Weight_Code = Prefix + "_Weight"
					RPE_Code = Prefix + "_RPE" 

					Tempo_Code_1 = Prefix + "_Tempo_1"
					Tempo_Code_2 = Prefix + "_Tempo_2"
					Tempo_Code_3 = Prefix + "_Tempo_3"

					Set_Label = "B" + str(n + 1)

					Filled = True

					if Rep_Code in request.GET.keys():
						_Reps = request.GET[Rep_Code]
						if _Reps == "":
							Filled = False
					if Weight_Code in request.GET.keys():
						_Weight = request.GET[Weight_Code]
						if _Weight == "":
							Filled = False
					if RPE_Code in request.GET.keys():
						_RPE = request.GET[RPE_Code]
						if _RPE == "":
							Filled = False
					if Tempo_Code_1 in request.GET.keys():
						Tempo_1 = request.GET[Tempo_Code_1] 
						Tempo_2 = request.GET[Tempo_Code_2] 
						Tempo_3 = request.GET[Tempo_Code_3] 
						_Tempo = Tempo_1 + "-" + Tempo_2 + "-" + Tempo_3
						if Tempo_1 == "" or Tempo_2 == "" or Tempo_3 == "":
							Filled = False

					if Filled:
						if Alloy_Sub:
							Set_Label = "A" + str(n + 1)
						else:
							Set_Label = "R" + str(n + 1)


					Stats = Set_Label + "," + _Reps + "," + _Weight + "," + _RPE + "," + _Tempo + "/"
					# print("Subworkout " + _Sub.Exercise.Name + " Set " + str(n) + " Stats: " + str(Stats.split(",")))
					Set_Stats += Stats

				Set_List = Set_Stats.split("/")
				print("Set_List: " + str(Set_List))
				print("Initial Sets Value: " + str(Initial_Sets))
				Set_List.remove('')
				
				# for Set in Set_List:
				# 	print(Set.split(",")[0])
				# 	print("	Reps: " + Set.split(",")[1])
				# 	print("	Weights: " + Set.split(",")[2])
				# 	print("	RPE: " + Set.split(",")[3])
				# 	print("	Tempo: " + Set.split(",")[4])
				# _Sub.Set_Stats = ""
				_Sub.Set_Stats += "/" + "/".join(Set_List)
				_Sub.save()

				Last_Set = ["", "", "", "", ""]
				if len(Set_List) > 1: 
					Last_Set = Set_List[-1].split(",")

				print(_Sub.Exercise_Type + " Last Set: ")
				print("	Reps: " + Last_Set[1])
				print("	Weights: " + Last_Set[2])
				print("	RPE: " + Last_Set[3])
				print("	Tempo: " + Last_Set[4])

				_Reps_Estimate = _Sub.Reps
				_Weight_Estimate = _Stat.Max
				# _RPE_Estimate = int(_Sub.RPE)
				_RPE_Estimate = 10

				if Last_Set[2] != "":
					_Weight_Estimate = int(Last_Set[2])
				if Last_Set[1] != "":
					_Reps_Estimate = int(Last_Set[1])
				if Last_Set[3] != "":
					if Last_Set[3] == "X":
						_RPE_Estimate = 10
						_Weight_Estimate = _Weight_Estimate*0.75
					else:
						_RPE_Estimate = float(Last_Set[3])

				if _RPE_Estimate > 10:
					_RPE_Estimate = 10

				_Stat.Max = Get_Max(_Weight_Estimate, _Reps_Estimate, _RPE_Estimate)
				_Stat.save()

				if Get_Alloy_Pressed and request.session["Show_Alloy_Type"] == _Sub.Exercise_Type:
					_Stat.Alloy_Weight = Get_Weight(_Stat.Max, _Sub.Money + 1, 10)
					_Stat.save()
					print("New Alloy Weight: " + str(_Stat.Alloy_Weight))

				if request.GET.get("Submit_Workout"):
					if Alloy_Sub and _Sub.Show_Alloy:
						_Rep_Code = _Sub.Exercise_Type + "Alloy_Set_Reps"
						_Tempo_1_Code = _Sub.Exercise_Type + "Alloy_Set_Tempo_1"
						_Tempo_2_Code = _Sub.Exercise_Type + "Alloy_Set_Tempo_2"
						_Tempo_3_Code = _Sub.Exercise_Type + "Alloy_Set_Tempo_3"
						Tempo = ""
						if _Tempo_1_Code in request.GET.keys():
							_Tempo_1 = request.GET[_Tempo_1_Code]
							_Tempo_2 = request.GET[_Tempo_2_Code]
							_Tempo_3 = request.GET[_Tempo_3_Code]
							Tempo = _Tempo_1 + "-" + _Tempo_2 + "-" + _Tempo_3
						print("Checking Alloy")
						Performed_Reps = request.GET[_Rep_Code]
						_Weight = _Stat.Alloy_Weight

						print("ALLOY SET STATS: ")
						print("	REPS: " + str(Performed_Reps))
						print("	WEIGHT: " + str(_Stat.Alloy_Weight))
						print("	TEMPO: " + str(Tempo))
						print(" VS REQUIREMENT: " + str(_Stat.Alloy_Reps))
						if int(Performed_Reps) >= _Stat.Alloy_Reps:
							_Stat.Level_Up = True
							_Stat.Failed = False
							_Stat.save()
						elif int(Performed_Reps) < _Stat.Alloy_Reps:
							_Stat.Level_Up = False
							_Stat.Failed = True
							_Stat.save()

						Set_Label = "A" + str(_Sub.Sets)
						Stat_String = Set_Label + "," + str(Performed_Reps) + "," + str(_Weight) + ",10," + Tempo
						Stat_List = Stat_String.split("/")
						# Stat_List.remove('')
						_Sub.Set_Stats += "/" + Stat_String
						_Sub.save()
				# 	Stats = Set_Label + "," + _Reps + "," + _Weight + "," + _RPE + "," + _Tempo + "/"
				# 	# print("Subworkout " + _Sub.Exercise.Name + " Set " + str(n) + " Stats: " + str(Stats.split(",")))
				# 	Set_Stats += Stats

				# Set_List = Set_Stats.split("/")
				# print("Set_List: " + str(Set_List))
				# print("Initial Sets Value: " + str(Initial_Sets))
				# Set_List.remove('')

						# _Set_Label = "A" + str(_Sub.Reps)
						# _Stat_String = _Set_Label + "," + Performed_Reps + "," + str(_Weight) + "," + "10" + "," + Tempo + "/"
						# _Sub.Set_Stats += "/" + "/".join(_Stat_String)
						# _Sub.save()



				if request.GET.get("Get_Alloy"):
					_Workout.Show_Alloy_Weights = True
					_Workout.save()
					if Alloy_Sub:
						_Stat.Alloy_Weight = Get_Weight(_Stat.Max, _Reps_Estimate + 1, 10) 
				elif not Alloy_Sub and request.GET.get("Submit_Workout"):
					print("Estimated Max: " + str(_Stat.Max))
					print(" From (Weight/Reps/RPE): " + str(_Weight_Estimate) + "/" + str(_Reps_Estimate) + "/" + str(_RPE_Estimate))
					_Workout.Submitted = True
					_Workout.save()
				elif Alloy_Sub and request.GET.get("Submit_Workout"):
					print("Alloy Sub Submitted Workout")
					Reps_Test = 0
					print(Last_Set)
					print("Money: " + str(_Sub.Money))
					print(Last_Set[1])
					if Last_Set[1] != "":
						Reps_Test = int(Last_Set[1])
					
					# if Reps_Test >= _Sub.Money:
					# 	print("Alloy Set Passed: " + str(Reps_Test) + " > " + str(_Sub.Money))
					# 	_Stat.Level_Up = True
					# 	_Stat.Failed = False
					# 	if _Stat.Core == False and _Stat.Level < _Member.Level + 2:
					# 		_Stat.Level += 1
					# 	_Stat.save()

					# elif Reps_Test < _Sub.Money:
					# 	_Stat.Failed = True
					# 	_Stat.save()					

				# print("Sub Set Stats Final: " + str(_Sub.Set_Stats.split("/")))
				# print("Sub Set List: " + str(_Sub.Set_Stats.split("/")))
				# print("Last Set: " + str(_Sub.Set_Stats.split("/")[-2]))

				if _Workout.Template.Last:
					Check_Level_Up(_Member)					
					# if Check_Level_Up(_Member):
					# 	return HttpResponseRedirect("/level-up")

				# if _Workout.Last:

				# if Workout.First:
				# if Workout.Last:
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

			_Workout.Submitted = True
			_Workout.save()			
			return HttpResponseRedirect("/userpage")

		print(str(Workout_Date.strftime("%y/%m/%d")))
		print(str(datetime.now().strftime("%y/%m/%d")))			

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


