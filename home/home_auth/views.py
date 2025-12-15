from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from home_auth.models import CustomUser
from student.models import Student, Discipline, Batch, Semester, Section
from teachers.models import Teacher
from student.models import Discipline
from head.models import AdminProfile

def manage_students_view(request):
    discipline_id = request.GET.get('discipline')
    batch_id = request.GET.get('batch')
    semester_id = request.GET.get('semester')
    section_id = request.GET.get('section')

    students = Student.objects.select_related('discipline', 'batch', 'semester', 'section').all()

    if discipline_id:
        students = students.filter(discipline_id=discipline_id)
    if batch_id:
        students = students.filter(batch_id=batch_id)
    if semester_id:
        students = students.filter(semester_id=semester_id)
    if section_id:
        students = students.filter(section_id=section_id)

    if request.method == "POST":
        student_id = request.POST.get("student_id")
        student = get_object_or_404(Student, id=student_id)

        if not student.user:
            username = student.email.split('@')[0]
            random_password = get_random_string(10)

            user = CustomUser.objects.create_user(
                username=username,
                email=student.email,
                password=random_password,
                is_student=True
            )

            student.user = user
            student.save()

            send_mail(
                "Your Account Details",
                f"Username: {username}\nPassword: {random_password}",
                settings.DEFAULT_FROM_EMAIL,
                [student.email],
                fail_silently=False,
            )
            messages.success(request, f"Account created and password sent to {student.email}")
        else:
            messages.info(request, f"User already exists for {student.email}")

        return redirect("manage_students")

    context = {
        "disciplines": Discipline.objects.all(),
        "batches": Batch.objects.all(),
        "semesters": Semester.objects.all(),
        "sections": Section.objects.all(),
        "students": students,
    }

    return render(request, "authentication/register.html", context)

def manage_teachers_view(request):
    teachers = Teacher.objects.all()

    if request.method == "POST":
        teacher_id = request.POST.get("teacher_id")
        teacher = get_object_or_404(Teacher, id=teacher_id)

        if not teacher.user:
            username = teacher.email.split('@')[0]
            random_password = get_random_string(10)

            user = CustomUser.objects.create_user(
                username=username,
                email=teacher.email,
                password=random_password,
                is_teacher=True
            )

            teacher.user = user
            teacher.save()

            send_mail(
                "Your Account Details",
                f"Welcome to the Learning Management System.\n\n"
                f"Your account has been created.\n"
                f"Username: {username}\n"
                f"Temporary Password: {random_password}\n"
                f"You can change your password within 24 hours.\n"
                f"After that, password change will be locked.",
                settings.DEFAULT_FROM_EMAIL,
                [teacher.email],
                fail_silently=False,
            )
            messages.success(request, f"Account created and login details sent to {teacher.email}")
        else:
            messages.info(request, f"User already exists for {teacher.email}")

        return redirect("manage_teachers")

    context = {
        "teachers": teachers,
    }

    return render(request, "authentication/register_teacher.html", context)
    


def manage_admins_view(request):

    discipline_id = request.GET.get('discipline')
    role_filter = request.GET.get('role')
    
    admins = AdminProfile.objects.select_related('user', 'discipline').all()
    
    if discipline_id:
        admins = admins.filter(discipline_id=discipline_id)
    if role_filter:
        admins = admins.filter(role=role_filter)

    if request.method == "POST":
        admin_id = request.POST.get("admin_id")
        admin = get_object_or_404(AdminProfile, id=admin_id)

        if not admin.user:
            # Create user account for admin
            username = admin.email.split('@')[0]
            random_password = get_random_string(10)

            user = CustomUser.objects.create_user(
                username=username,
                email=admin.email,
                password=random_password,
                is_staff=True  # Admin users should have staff privileges
            )

            admin.user = user
            admin.save()

            # Send email with login credentials
            send_mail(
                "Your Admin Account Details",
                f"Welcome to the Learning Management System.\n\n"
                f"Your admin account has been created.\n"
                f"Role: {admin.get_role_display()}\n"
                f"Username: {username}\n"
                f"Temporary Password: {random_password}\n\n"
                f"Please change your password after first login for security.",
                settings.DEFAULT_FROM_EMAIL,
                [admin.email],
                fail_silently=False,
            )
            messages.success(request, f"Admin account created and login details sent to {admin.email}")
        else:
            messages.info(request, f"User account already exists for {admin.email}")

        return redirect("manage_admins")

    context = {
        "admins": admins,
        "disciplines": Discipline.objects.all(),
        "role_choices": AdminProfile._meta.get_field('role').choices,
    }

    return render(request, "authentication/register_admin.html", context)
