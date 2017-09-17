from django.conf.urls import url
from django.contrib import admin
# from Users.views import Home, Member_Home, Admin, Test, User_Page, Workout_Update, Videos, AdminExercises, RPE_Update, SignUp_Confirmation, Welcome, Past_Workouts, User_Profile, Level_Up

from Users.views import *
from Users.admin_views import *
from Users.admin_video_views import *
from Users.test_views import *
from Users.sign_up_views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^admin-login/', Admin_Login, name='AdminUsers'),

    url(r'^admin-users/', Admin_Users, name='AdminUsers'),
    url(r'^admin-users-view-profile/', Admin_User_Profile, name='AdminUser_Profile'),

    url(r'^admin-workouts/', Admin_Workouts, name='Home'),
    url(r'^admin-workouts-2/', Admin_Workouts_2, name='Home'),
    url(r'^admin-workouts-3/', Admin_Workouts_3, name='Home'),
    url(r'^admin-workouts-4/', Admin_Workouts_4, name='Home'),

    url(r'^admin-exercises/', AdminExercises, name='Home'),

    url(r'^admin-videos/', Admin_Videos, name='Home'),
    url(r'^admin-videos-2/', Admin_Videos_2, name=''),    
    url(r'^admin-videos-library/', Admin_Videos_Library, name='Home'),
    url(r'^admin-videos-library-edit/', Admin_Videos_Edit, name='Home'),


    url(r'^$', Home, name='Home'),
    url(r'^sign-up-confirmation/', SignUp_Confirmation, name='SignUpConfirmation'),
    url(r'^welcome/', Welcome, name='Welcome'),

    url(r'^welcome/', SignUp_Confirmation, name='SignUpConfirmation'),
    url(r'^member-home/', Member_Home, name='Home'),
    url(r'^test/', Test, name='Test'),

    url(r'^tutorial/', Tutorial, name="tutorial"),

    url(r'^userpage/', User_Page, name="userpage"),

    url(r'^userpage-alloy/', User_Page_Alloy, name="userpage_alloy"),

    url(r'^level-up/', Level_Up, name="levelup"),
    url(r'^userpageUpdate/', Workout_Update, name="userpageUpdate"),
    url(r'^userpageRPEUpdate/', RPE_Update, name="userpageRPEUpdate"),
    url(r'^userprofile/', User_Profile, name="userprofile"),
    url(r'^past-workouts/', Past_Workouts, name="pastworkouts"),
    url(r'^videos/', Videos, name="videos"),

    url(r'^logout/', Logout, name='logout'),

]
