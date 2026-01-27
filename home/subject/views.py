from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Subject ,SubjectAssign
from student.models import Student
from Academic.models import Discipline,Batch,Semester,Section

from teachers.models import Teacher
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404


def add_subject(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        semester = request.POST.get('semester')
        credit_hours = request.POST.get('credit_hours')
        description = request.POST.get('description')
        subject_type = request.POST.get('subject_type')
        discipline_id = request.POST.get('discipline')

        # Convert semester and credit_hours to integers safely
        semester = int(semester) if semester else None
        credit_hours = int(credit_hours) if credit_hours else None

        # Get the Discipline instance
        discipline = Discipline.objects.get(id=discipline_id) if discipline_id else None

        # Check if subject with same code and semester exists
        if Subject.objects.filter(code=code, semester=semester).exists():
            messages.error(request, "Error: This subject already exists for the selected semester.")
        else:
            Subject.objects.create(
                name=name,
                code=code,
                subject_id=f"{code}-{semester}",
                semester=semester,
                credit_hours=credit_hours,
                description=description,
                subject_type=subject_type,
                desciplain=discipline,
                is_active=True
            )
            messages.success(request, "Subject saved successfully.")
            # return redirect('view_subject')

    context = {
        'semester_choices': Subject.SEMESTER_CHOICES,
        'subject_type_choices': Subject.SUBJECT_TYPE_CHOICES,
        'disciplines': Discipline.objects.all()
    }
    return render(request, 'subject/add-subject.html', context)


def view_subject(request):
    subjects = Subject.objects.all().order_by('name', 'semester')
    disciplines = Discipline.objects.all()

    semester = request.GET.get('semester')
    subject_type = request.GET.get('subject_type')
    is_active = request.GET.get('is_active')
    discipline_id = request.GET.get('discipline')

    # Filter by semester
    if semester:
        subjects = subjects.filter(semester=semester)

    # Filter by subject type
    if subject_type:
        subjects = subjects.filter(subject_type=subject_type)

    # Filter by active/inactive status
    if is_active:
        subjects = subjects.filter(is_active=(is_active.lower() == 'true'))

    # Filter by discipline
    if discipline_id:
        selected_discipline = get_object_or_404(Discipline, id=discipline_id)
        subjects = subjects.filter(desciplain=selected_discipline)
    else:
        selected_discipline = None

    paginator = Paginator(subjects, 10)
    page = request.GET.get('page')
    subjects = paginator.get_page(page)

    context = {
        'subjects': subjects,
        'semester_choices': Subject.SEMESTER_CHOICES,
        'subject_type_choices': Subject.SUBJECT_TYPE_CHOICES,
        'disciplines': disciplines,
        'selected_discipline': selected_discipline,
    }

    return render(request, 'subject/subject-list.html', context)

@login_required
def stu_subject(request):
    try:
        student = request.user.student
    except Student.DoesNotExist:
        return HttpResponse("Student profile not found. Please contact admin.")

    subjects = Subject.objects.filter(
        semester=student.semester.number  
    )

    return render(request, "students/subject.html", {"subjects": subjects})

    

# @login_required
def add_subject_assign(request):
    if request.method == "POST":
        # Get all form data
        teacher_id = request.POST.get("teacher")
        subject_id = request.POST.get("subject")
        batch_id = request.POST.get("batch")
        semester_id = request.POST.get("semester")
        section_id = request.POST.get("section")
        discipline_id = request.POST.get("disciplines")  # This should match the 'name' attribute
        
        # Debug: Print what you're getting
        print("=" * 50)
        print("FORM DATA RECEIVED:")
        print(f"Teacher: {teacher_id}")
        print(f"Subject: {subject_id}")
        print(f"Batch: {batch_id}")
        print(f"Semester: {semester_id}")
        print(f"Section: {section_id}")
        print(f"Discipline: {discipline_id}")
        print("=" * 50)
        
        # Check if any field is empty
        if not all([teacher_id, subject_id, batch_id, semester_id, section_id, discipline_id]):
            missing_fields = []
            if not teacher_id: missing_fields.append("Teacher")
            if not subject_id: missing_fields.append("Subject")
            if not batch_id: missing_fields.append("Batch")
            if not semester_id: missing_fields.append("Semester")
            if not section_id: missing_fields.append("Section")
            if not discipline_id: missing_fields.append("Discipline")
            
            messages.error(request, f"Missing fields: {', '.join(missing_fields)}")
            return redirect("subject:add_subject_assign")
        
        # Get objects
        teacher = get_object_or_404(Teacher, id=teacher_id)
        subject = get_object_or_404(Subject, id=subject_id)
        batch = get_object_or_404(Batch, id=batch_id)
        semester = get_object_or_404(Semester, id=semester_id)
        section = get_object_or_404(Section, id=section_id)
        discipline = get_object_or_404(Discipline, id=discipline_id)

        # Check if assignment already exists
        if SubjectAssign.objects.filter(
            teacher=teacher,
            subject=subject,
            batch=batch,
            semester=semester,
            section=section,
            discipline=discipline
        ).exists():
            messages.warning(request, "This subject is already assigned.")
        else:
            SubjectAssign.objects.create(
                teacher=teacher,
                subject=subject,
                batch=batch,
                semester=semester,
                section=section,
                discipline=discipline,
                is_active=True
            )
            messages.success(request, "Subject assigned successfully.")
            return redirect("subject:show_subject_assign")

    context = {
        "teachers": Teacher.objects.all(),
        "subjects": Subject.objects.filter(is_active=True),
        "batches": Batch.objects.all(),
        "semesters": Semester.objects.all(),
        "sections": Section.objects.all(),
        "disciplines": Discipline.objects.all()
    }

    return render(request, "subject/add-subject-assign.html", context)
def show_subject_assign(request):
    # Now include 'discipline' since it exists in the model
    assigns = SubjectAssign.objects.select_related(
        "teacher", 
        "subject", 
        "batch", 
        "semester", 
        "section",
        "discipline"  # Add this - now it exists in the model
    ).order_by('-id')
    
    context = {
        "assigns": assigns
    }
    return render(request, "subject/show-subject-assign-record.html", context)