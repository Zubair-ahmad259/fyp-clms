from django.contrib import admin
from .models import Subject

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin interface configuration for the Subject model"""
    
    # Fields to display in the list view
    list_display = (
        'code', 
        'name', 
        'subject_type', 
        'semester', 
        'desciplain',
        'credit_hours',
        'is_active'
    )
    
    # Fields that can be filtered in the admin
    list_filter = (
        'subject_type', 
        'semester', 
        'is_active',
        'desciplain'
    )
    
    # Fields that can be searched
    search_fields = (
        'code', 
        'name', 
        'subject_id',
        'description'
    )
    
    # Fields that are read-only
    readonly_fields = (
        'created_at', 
        'updated_at'
    )
    
    # Fieldsets for the detail view
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'code', 
                'name', 
                'subject_id',
                'description'
            )
        }),
        ('Academic Details', {
            'fields': (
                'subject_type',
                'semester',
                'desciplain',
                'credit_hours'
            )
        }),
        ('Status', {
            'fields': (
                'is_active',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    # Pre-populate fields based on other fields
    prepopulated_fields = {'subject_id': ('code',)}
    
    # Default ordering
    ordering = ('semester', 'code')
    
    # Add a date hierarchy
    date_hierarchy = 'created_at'

    from django.contrib import admin
from .models import SubjectAssign

@admin.register(SubjectAssign)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'batch', 'semester', 'section', 'assigned_date', 'is_active')
    list_filter = ('batch', 'semester', 'section', 'is_active')
    search_fields = (
        'teacher__first_name',
        'teacher__last_name',
        'subject__name',
        'batch__name',
        'section__name',
    )
    ordering = ('teacher', 'subject')
