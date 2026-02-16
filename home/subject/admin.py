# admin.py
from django.contrib import admin
from django import forms
from .models import Subject, SubjectAssign
from django.utils.html import format_html
import pandas as pd
from django.http import HttpResponse
import csv


class SubjectAdminForm(forms.ModelForm):
    prerequisites = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select prerequisite subjects (must be from previous semesters)"
    )
    
    class Meta:
        model = Subject
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        semester = cleaned_data.get('semester')
        prerequisites = cleaned_data.get('prerequisites')
        
        if semester and prerequisites:
            for prereq in prerequisites:
                if prereq.semester.number >= semester.number:
                    raise forms.ValidationError(
                        f"Prerequisite {prereq.code} cannot be from same or higher semester. "
                        f"Current subject semester: {semester.number}, Prerequisite semester: {prereq.semester.number}"
                    )
        
        return cleaned_data


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    form = SubjectAdminForm
    list_display = ('code', 'name', 'semester_display', 'section', 'subject_type', 'credit_hours', 'desciplain', 'prereq_count', 'is_active')
    list_filter = ('semester', 'section', 'subject_type', 'desciplain', 'is_active')
    search_fields = ('code', 'name', 'description')
    filter_horizontal = ('prerequisites',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'semester', 'section', 'desciplain', 'subject_type')
        }),
        ('Academic Details', {
            'fields': ('credit_hours',)
        }),
        ('Prerequisites', {
            'fields': ('prerequisites',),
            'description': 'Select subjects that must be completed before this subject'
        }),
        ('Additional Information', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['export_as_csv', 'export_as_excel']
    
    def semester_display(self, obj):
        return f"Sem {obj.semester.number}"
    semester_display.short_description = 'Semester'
    semester_display.admin_order_field = 'semester__number'
    
    def prereq_count(self, obj):
        return obj.prerequisites.count()
    prereq_count.short_description = 'Prerequisites'
    
    # Export as CSV
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields if field.name != 'prerequisites']
        field_names.extend(['prerequisite_codes', 'semester_number', 'section_name'])
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=subjects_export.csv'
        writer = csv.writer(response)
        
        writer.writerow(field_names)
        for obj in queryset:
            row = []
            for field in field_names:
                if field == 'prerequisite_codes':
                    prereqs = obj.prerequisites.all()
                    prereq_codes = ", ".join([p.code for p in prereqs])
                    row.append(prereq_codes)
                elif field == 'semester_number':
                    row.append(obj.semester.number if obj.semester else '')
                elif field == 'section_name':
                    row.append(obj.section.name if obj.section else '')
                elif field == 'semester':
                    row.append(str(obj.semester))
                elif field == 'section':
                    row.append(str(obj.section) if obj.section else '')
                elif field == 'desciplain':
                    row.append(str(obj.desciplain))
                else:
                    try:
                        row.append(getattr(obj, field))
                    except AttributeError:
                        row.append('')
            
            writer.writerow(row)
        
        return response
    export_as_csv.short_description = "Export Selected as CSV"
    
    # Export as Excel
    def export_as_excel(self, request, queryset):
        meta = self.model._meta
        
        # Prepare data
        data = []
        for obj in queryset:
            obj_data = {}
            for field in meta.fields:
                if field.name != 'prerequisites':
                    if field.name == 'semester':
                        obj_data['semester'] = f"Sem {obj.semester.number}"
                        obj_data['semester_number'] = obj.semester.number
                    elif field.name == 'section':
                        obj_data['section'] = obj.section.name if obj.section else ''
                    elif field.name == 'desciplain':
                        obj_data['discipline'] = str(obj.desciplain)
                    elif field.name == 'subject_type':
                        obj_data['subject_type'] = obj.get_subject_type_display()
                    else:
                        obj_data[field.name] = getattr(obj, field.name)
            
            # Add prerequisites as comma-separated codes
            prereqs = obj.prerequisites.all()
            obj_data['prerequisites'] = ", ".join([p.code for p in prereqs])
            data.append(obj_data)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Reorder columns for better readability
        column_order = ['code', 'name', 'semester', 'semester_number', 'section', 'discipline', 
                       'subject_type', 'credit_hours', 'prerequisites', 'description', 'is_active']
        
        # Filter columns that exist in the DataFrame
        available_columns = [col for col in column_order if col in df.columns]
        remaining_columns = [col for col in df.columns if col not in available_columns]
        df = df[available_columns + remaining_columns]
        
        # Create HTTP response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=subjects_export.xlsx'
        
        # Write to Excel
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Subjects', index=False)
        
        return response
    export_as_excel.short_description = "Export Selected as Excel"
    
    # Custom admin view for import
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['import_url'] = '/admin/subject/subject/import/'  # Customize as needed
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(SubjectAssign)
class SubjectAssignAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'batch', 'semester_display', 'section', 'discipline', 'assigned_date', 'is_active')
    list_filter = ('batch', 'semester', 'section', 'discipline', 'is_active')
    search_fields = ('subject__code', 'subject__name', 'teacher__name')
    list_per_page = 20
    
    def semester_display(self, obj):
        return f"Sem {obj.semester.number}"
    semester_display.short_description = 'Semester'
    semester_display.admin_order_field = 'semester__number'