from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Subject ,SubjectAssign
from student.models import Student,Discipline,Batch,Semester,Section,Parent
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
        teacher_id = request.POST.get("teacher")
        subject_id = request.POST.get("subject")
        batch_id = request.POST.get("batch")
        semester_id = request.POST.get("semester")
        section_id = request.POST.get("section")
        discipline=request.POST.get("disciplines")

        # Validation for missing fields
        if not all([teacher_id, subject_id, batch_id, semester_id, section_id,discipline]):
            messages.error(request, "All fields are required.")
            return redirect("view_subject")

        teacher = get_object_or_404(Teacher, id=teacher_id)
        subject = get_object_or_404(Subject, id=subject_id)
        batch = get_object_or_404(Batch, id=batch_id)
        semester = get_object_or_404(Semester, id=semester_id)
        section = get_object_or_404(Section, id=section_id)
        discipline=get_object_or_404(Discipline,id=discipline)

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

    context = {
        "teachers": Teacher.objects.all(),
        "subjects": Subject.objects.filter(is_active=True),
        "batches": Batch.objects.all(),
        "semesters": Semester.objects.all(),
        "sections": Section.objects.all(),
        "discplines":Discipline.objects.all()
    }

    return render(request, "subject/add-subject-assign.html", context)

def show_subject_assign(request):
    assigns = SubjectAssign.objects.select_related("teacher","subject","section",'semester','discplines','batch').order_by('-id')
    context={
        "assigns": assigns
    }
    return redirect(request,"subject/show-subject-assign-record.html",context)

