from django.contrib import admin
from django.urls import path,include
from . import views

app_name = 'subjects'

urlpatterns = [
    path("",views.view_subject,name="view_subject"),
    path("add/",views.add_subject,name="add_subject"),
    path('stu/', views.stu_subject, name='stu_subject'),
    path('add-subject-assign/', views.add_subject_assign, name='add_subject_assign'),
    path('asssign-record/', views.show_subject_assign, name='show_subject_assign'),



]