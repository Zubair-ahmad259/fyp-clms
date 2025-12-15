from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.manage_students_view, name='signup'),
        path('manage_teachers_view/', views.manage_teachers_view, name='manage_teachers_view'),

    path('manage_admins_view/', views.manage_admins_view, name='manage_admins_view'),
    # path('logout/', views.logout_view, name='logout'),
    # path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    # path('reset-password/<str:token>/', views.reset_password_view, name='reset_password'),
]
