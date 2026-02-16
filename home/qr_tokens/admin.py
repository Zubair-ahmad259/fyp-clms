# tokenization/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Token, AttendanceToken, ExamToken, PermissionToken,
    TokenComment, TokenWorkflow, TokenNotification,
    TokenCategory, TokenRule, TokenStatistics
)

class TokenAdmin(admin.ModelAdmin):
    list_display = [
        'token_number', 'student', 'token_type', 
        'status', 'priority', 'created_date', 'assigned_to'
    ]
    list_filter = [
        'token_type', 'status', 'priority', 
        'batch', 'semester', 'is_urgent'
    ]
    search_fields = [
        'token_number', 'student__student_id', 
        'student__first_name', 'student__last_name', 'title'
    ]
    readonly_fields = ['created_at', 'updated_at', 'token_number']
    ordering = ['-created_date']
    date_hierarchy = 'created_date'
    list_per_page = 20

class AttendanceTokenAdmin(admin.ModelAdmin):
    list_display = [
        'token_number', 'student', 'attendance_date', 
        'subject', 'original_status', 'requested_status', 'status'
    ]
    list_filter = ['subject', 'status', 'attendance_date']
    search_fields = [
        'token__token_number', 'student__student_id', 
        'subject__name', 'subject__code'
    ]
    readonly_fields = ['token_number']

class ExamTokenAdmin(admin.ModelAdmin):
    list_display = [
        'token_number', 'student', 'exam', 
        'request_type', 'status', 'is_medical_case'
    ]
    list_filter = ['request_type', 'status', 'is_medical_case']
    search_fields = [
        'token__token_number', 'student__student_id',
        'exam__exam_type'
    ]

class PermissionTokenAdmin(admin.ModelAdmin):
    list_display = [
        'token_number', 'student', 'permission_type',
        'start_date', 'end_date', 'status'
    ]
    list_filter = ['permission_type', 'status', 'start_date']
    search_fields = [
        'token__token_number', 'student__student_id',
        'permission_type'
    ]

class TokenCommentInline(admin.TabularInline):
    model = TokenComment
    extra = 1
    readonly_fields = ['created_at']

class TokenWorkflowInline(admin.TabularInline):
    model = TokenWorkflow
    extra = 1
    readonly_fields = ['created_at', 'updated_at']

class TokenCommentAdmin(admin.ModelAdmin):
    list_display = ['token', 'author', 'created_at', 'is_internal_note']
    list_filter = ['is_internal_note', 'author', 'created_at']
    search_fields = ['token__token_number', 'comment']
    readonly_fields = ['created_at', 'updated_at']

class TokenWorkflowAdmin(admin.ModelAdmin):
    list_display = [
        'token', 'step_name', 'status', 
        'assigned_to', 'completed_by', 'order'
    ]
    list_filter = ['status', 'step_name', 'is_required']
    search_fields = ['token__token_number', 'step_name']
    readonly_fields = ['created_at', 'updated_at']

class TokenNotificationAdmin(admin.ModelAdmin):
    list_display = ['token', 'recipient', 'notification_type', 'created_at', 'is_read']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['token__token_number', 'recipient__student_id']
    readonly_fields = ['created_at']

class TokenCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'default_priority', 'sla_days', 'is_active']
    list_filter = ['is_active', 'default_priority']
    search_fields = ['name', 'description']
    ordering = ['name']

class TokenRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'priority', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['-priority', 'name']
    readonly_fields = ['created_at', 'updated_at']

class TokenStatisticsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'total_tokens', 'pending_tokens',
        'resolved_tokens', 'overdue_tokens'
    ]
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 30
    ordering = ['-date']
    date_hierarchy = 'date'

# Register models
admin.site.register(Token, TokenAdmin)
admin.site.register(AttendanceToken, AttendanceTokenAdmin)
admin.site.register(ExamToken, ExamTokenAdmin)
admin.site.register(PermissionToken, PermissionTokenAdmin)
admin.site.register(TokenComment, TokenCommentAdmin)
admin.site.register(TokenWorkflow, TokenWorkflowAdmin)
admin.site.register(TokenNotification, TokenNotificationAdmin)
admin.site.register(TokenCategory, TokenCategoryAdmin)
admin.site.register(TokenRule, TokenRuleAdmin)
admin.site.register(TokenStatistics, TokenStatisticsAdmin)