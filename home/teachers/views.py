from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from .models import Teacher  # Changed to uppercase model name
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.text import slugify

def add_teacher(request):
    if request.method == "POST":
        try:
            # Get all data from POST
            data = {
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
                'father_name': request.POST.get('father_name'),
                'teacher_id': request.POST.get('teacher_id'),
                'gender': request.POST.get('gender'),
                'date_of_birth': request.POST.get('date_of_birth'),
                'salary': request.POST.get('salary'),
                'religion': request.POST.get('religion'),
                'joining_date': request.POST.get('joining_date'),
                'mobile_number': request.POST.get('mobile_number'),
                'email': request.POST.get('email'),
                'field': request.POST.get('field'),
                'experience': request.POST.get('experience'),  # Fixed spelling from 'experince'
                'teacher_image': request.FILES.get('teacher_image'),
            }
            
            # Create teacher
            teacher = Teacher.objects.create(**data)
            
            # Generate and save slug if not auto-generated in model
            if not teacher.slug:
                teacher.slug = slugify(f"{teacher.first_name}-{teacher.last_name}-{teacher.teacher_id}")
                teacher.save()
            
            messages.success(request, "Teacher added successfully")
            return redirect('teacher_list')
            
        except ValidationError as e:
            messages.error(request, f"Validation Error: {e}")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
    
    return render(request, "teacher/add-teacher.html")

def teacher_list(request):
    teachers = Teacher.objects.all().order_by('last_name', 'first_name')  # Added ordering
    context = {
        "teachers": teachers
    }
    return render(request, "teacher/teachers.html", context)

def edit_teacher(request, teacher_id):
    teacher_obj = get_object_or_404(Teacher, teacher_id=teacher_id)
    
    if request.method == "POST":
        try:
            # Update fields
            teacher_obj.first_name = request.POST.get('first_name')
            teacher_obj.last_name = request.POST.get('last_name')
            teacher_obj.father_name = request.POST.get('father_name')
            teacher_obj.teacher_id = request.POST.get('teacher_id')
            teacher_obj.gender = request.POST.get('gender')
            teacher_obj.date_of_birth = request.POST.get('date_of_birth')
            teacher_obj.salary = request.POST.get('salary')
            teacher_obj.religion = request.POST.get('religion')
            teacher_obj.joining_date = request.POST.get('joining_date')
            teacher_obj.mobile_number = request.POST.get('mobile_number')
            teacher_obj.email = request.POST.get('email')
            teacher_obj.field = request.POST.get('field')
            teacher_obj.experience = request.POST.get('experience')  # Fixed spelling
            
            # Handle image upload
            if 'teacher_image' in request.FILES:
                teacher_obj.teacher_image = request.FILES['teacher_image']
            
            teacher_obj.save()
            messages.success(request, "Teacher updated successfully")
            return redirect('teacher_list')
            
        except ValidationError as e:
            messages.error(request, f"Validation Error: {e}")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
    
    context = {
        "teacher": teacher_obj
    }
    return render(request, "teacher/edit-teacher.html", context)

def view_teacher(request, teacher_id):

    teacher_obj = get_object_or_404(Teacher, teacher_id=teacher_id)  # Changed to use slug instead of teacher_id
    context = {
        "teacher": teacher_obj
    }
    return render(request, "teacher/teacher-details.html", context)


