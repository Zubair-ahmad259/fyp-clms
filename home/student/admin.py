from django.contrib import admin
from .models import Batch, Semester, Section, Parent, Student,Discipline

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_year', 'end_year','discipline')
    search_fields = ('name',)
    list_filter = ('start_year', 'end_year')

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('number', 'description')
    search_fields = ('number', 'description')  # Added search_fields
    ordering = ('number',)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'batch', 'description')
    search_fields = ('name', 'batch__name')
    list_filter = ('batch',)

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('father_name', 'mother_name', 'father_contact')
    search_fields = ('father_name', 'mother_name', 'father_contact')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name','discipline',
'batch', 'semester', 'section')
    search_fields = ('student_id', 'first_name', 'last_name')
    list_filter = ('batch', 'semester', 'section', 'gender','discipline')
    autocomplete_fields = ['batch', 'semester', 'section','discipline']  # Requires search_fields in related admins
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'student_id', 'admission_number', 'gender', 'dob', 'image')
        }),
        ('Contact Information', {
            'fields': ('email', 'contact_number', 'address')
        }),
        ('Academic Information', {
            'fields': ('batch', 'semester', 'section','discipline')
        }),
        ('Parent Information', {
            'fields': ('parent',)
        }),
    )


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ('program', 'field')
    list_filter = ('program', 'field')
    search_fields = ('program', 'field')
    ordering = ('program', 'field')
