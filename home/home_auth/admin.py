from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CustomUser, PasswordResetRequest


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'is_student',
        'is_teacher',
        'is_admin',
        'is_authorized',
        'password_generated',
        'password_change_deadline'
    )
    list_filter = ('is_student', 'is_teacher', 'is_admin', 'is_authorized')
    search_fields = ('username', 'email')
    ordering = ('username',)


@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'token', 'created_at')
    search_fields = ('email', 'token')
    ordering = ('-created_at',)
