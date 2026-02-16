from django.shortcuts import render

# Create your views here.
# tokenization/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from datetime import date, timedelta
import json

from .models import (
    Token, AttendanceToken, ExamToken, PermissionToken,
    TokenComment, TokenNotification,
    TokenType, TokenStatus, PriorityLevel
)
from student.models import Student
from teachers.models import Teacher
from subject.models import Subject
from exam_mang.models import Exam
from Academic.models import Batch, Semester, Section, Discipline

# ========== PUBLIC VIEWS ==========

def index(request):
    """Home page"""
    return render(request, 'tokenization/index.html')

def token_types(request):
    """Show available token types"""
    token_types_info = [
        {
            'code': TokenType.PERMISSION,
            'name': 'Permission',
            'description': 'Request for leave, late entry, or special permissions',
            'icon': 'fas fa-calendar-check'
        },
        {
            'code': TokenType.ATTENDANCE,
            'name': 'Attendance Correction',
            'description': 'Request to correct attendance records',
            'icon': 'fas fa-user-check'
        },
        {
            'code': TokenType.EXAM,
            'name': 'Exam Token',
            'description': 'Request for makeup exams or special arrangements',
            'icon': 'fas fa-file-alt'
        },
        {
            'code': TokenType.MAKEUP,
            'name': 'Make-up Request',
            'description': 'Request for makeup classes or sessions',
            'icon': 'fas fa-redo-alt'
        },
        {
            'code': TokenType.FEE,
            'name': 'Fee Extension',
            'description': 'Request for fee payment extension',
            'icon': 'fas fa-money-bill-wave'
        },
        {
            'code': TokenType.LIBRARY,
            'name': 'Library Request',
            'description': 'Library book extension or special access',
            'icon': 'fas fa-book'
        },
        {
            'code': TokenType.OTHER,
            'name': 'Other Requests',
            'description': 'Any other type of request',
            'icon': 'fas fa-question-circle'
        }
    ]
    
    context = {
        'token_types': token_types_info
    }
    return render(request, 'tokenization/token_types.html', context)

# ========== STUDENT TOKEN MANAGEMENT ==========

def student_tokens(request, student_id=None):
    """View student's tokens"""
    if student_id:
        student = get_object_or_404(Student, id=student_id)
    else:
        # For demo, get first student
        student = Student.objects.first()
    
    if not student:
        messages.error(request, "No student found")
        return redirect('index')
    
    tokens = Token.objects.filter(student=student).order_by('-created_date')
    
    # Filtering
    token_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    
    if token_type:
        tokens = tokens.filter(token_type=token_type)
    if status:
        tokens = tokens.filter(status=status)
    
    context = {
        'student': student,
        'tokens': tokens,
        'token_types': TokenType.choices,
        'status_choices': TokenStatus.choices,
        'selected_type': token_type,
        'selected_status': status,
    }
    return render(request, 'tokenization/student_tokens.html', context)

def create_token(request, student_id=None):
    """Create a new token"""
    if student_id:
        student = get_object_or_404(Student, id=student_id)
    else:
        # For demo, get first student
        student = Student.objects.first()
    
    if not student:
        messages.error(request, "No student found")
        return redirect('index')
    
    if request.method == 'POST':
        try:
            # Get form data
            token_type = request.POST.get('token_type')
            title = request.POST.get('title')
            description = request.POST.get('description')
            priority = request.POST.get('priority')
            
            # Create token
            token = Token.objects.create(
                student=student,
                token_type=token_type,
                title=title,
                description=description,
                priority=priority,
                batch=student.batch,
                semester=student.semester,
                section=student.section,
                discipline=student.discipline,
                created_date=date.today(),
                due_date=date.today() + timedelta(days=7)
            )
            
            messages.success(request, f'Token #{token.token_number} created successfully!')
            return redirect('view_token', token_id=token.id)
            
        except Exception as e:
            messages.error(request, f'Error creating token: {str(e)}')
    
    # GET request - show form
    context = {
        'student': student,
        'token_types': TokenType.choices,
        'priority_choices': PriorityLevel.choices,
        'students': Student.objects.all()[:10],  # For demo dropdown
    }
    return render(request, 'tokenization/create_token.html', context)

def create_attendance_token(request, student_id=None):
    """Create attendance correction token"""
    if student_id:
        student = get_object_or_404(Student, id=student_id)
    else:
        student = Student.objects.first()
    
    if not student:
        messages.error(request, "No student found")
        return redirect('index')
    
    if request.method == 'POST':
        try:
            attendance_date = request.POST.get('attendance_date')
            subject_id = request.POST.get('subject')
            requested_status = request.POST.get('requested_status')
            reason = request.POST.get('reason')
            
            subject = get_object_or_404(Subject, id=subject_id)
            
            # Create attendance token
            token = AttendanceToken.objects.create(
                student=student,
                title=f'Attendance Correction - {subject.code}',
                description=reason,
                priority=PriorityLevel.MEDIUM,
                attendance_date=attendance_date,
                subject=subject,
                original_status='A',  # Assuming original was Absent
                requested_status=requested_status,
                reason_for_change=reason,
                batch=student.batch,
                semester=student.semester,
                section=student.section,
                discipline=student.discipline,
                created_date=date.today(),
                due_date=date.today() + timedelta(days=7)
            )
            
            messages.success(request, f'Attendance token #{token.token_number} created!')
            return redirect('view_token', token_id=token.id)
            
        except Exception as e:
            messages.error(request, f'Error creating attendance token: {str(e)}')
    
    # GET request
    subjects = Subject.objects.filter(semester=student.semester, discipline=student.discipline)
    
    context = {
        'student': student,
        'subjects': subjects,
        'attendance_status_choices': [('P', 'Present'), ('A', 'Absent')],
    }
    return render(request, 'tokenization/create_attendance_token.html', context)

def create_exam_token(request, student_id=None):
    """Create exam-related token"""
    if student_id:
        student = get_object_or_404(Student, id=student_id)
    else:
        student = Student.objects.first()
    
    if not student:
        messages.error(request, "No student found")
        return redirect('index')
    
    if request.method == 'POST':
        try:
            exam_id = request.POST.get('exam')
            request_type = request.POST.get('request_type')
            reason = request.POST.get('reason')
            requested_date = request.POST.get('requested_date')
            
            exam = get_object_or_404(Exam, id=exam_id)
            
            # Get subject mark component
            subject_mark_component = exam.subject_mark_component
            
            # Create exam token
            token = ExamToken.objects.create(
                student=student,
                title=f'{request_type} - {exam.exam_type}',
                description=reason,
                priority=PriorityLevel.HIGH,
                exam=exam,
                subject_mark_component=subject_mark_component,
                request_type=request_type,
                requested_exam_date=requested_date,
                batch=student.batch,
                semester=student.semester,
                section=student.section,
                discipline=student.discipline,
                created_date=date.today(),
                due_date=date.today() + timedelta(days=3)  # Shorter deadline for exam tokens
            )
            
            messages.success(request, f'Exam token #{token.token_number} created!')
            return redirect('view_token', token_id=token.id)
            
        except Exception as e:
            messages.error(request, f'Error creating exam token: {str(e)}')
    
    # GET request
    exams = Exam.objects.filter(
        subject_mark_component__batch=student.batch,
        subject_mark_component__semester=student.semester,
        subject_mark_component__discipline=student.discipline
    )
    
    context = {
        'student': student,
        'exams': exams,
        'request_types': [
            ('MAKEUP_EXAM', 'Make-up Exam'),
            ('EXAM_RESCHEDULE', 'Exam Reschedule'),
            ('SPECIAL_ASSISTANCE', 'Special Assistance'),
            ('OTHER_EXAM_REQUEST', 'Other Exam Request'),
        ]
    }
    return render(request, 'tokenization/create_exam_token.html', context)

def create_permission_token(request, student_id=None):
    """Create permission token"""
    if student_id:
        student = get_object_or_404(Student, id=student_id)
    else:
        student = Student.objects.first()
    
    if not student:
        messages.error(request, "No student found")
        return redirect('index')
    
    if request.method == 'POST':
        try:
            permission_type = request.POST.get('permission_type')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            reason = request.POST.get('reason')
            destination = request.POST.get('destination', '')
            
            # Create permission token
            token = PermissionToken.objects.create(
                student=student,
                title=f'{permission_type} Request',
                description=reason,
                priority=PriorityLevel.MEDIUM,
                permission_type=permission_type,
                start_date=start_date,
                end_date=end_date,
                start_time=start_time,
                end_time=end_time,
                reason_for_permission=reason,
                destination=destination,
                batch=student.batch,
                semester=student.semester,
                section=student.section,
                discipline=student.discipline,
                created_date=date.today(),
                due_date=date.today() + timedelta(days=2)  # Shorter deadline for permissions
            )
            
            messages.success(request, f'Permission token #{token.token_number} created!')
            return redirect('view_token', token_id=token.id)
            
        except Exception as e:
            messages.error(request, f'Error creating permission token: {str(e)}')
    
    # GET request
    context = {
        'student': student,
        'permission_types': [
            ('LEAVE', 'Leave Request'),
            ('LATE_ENTRY', 'Late Entry'),
            ('EARLY_EXIT', 'Early Exit'),
            ('OFF_CAMPUS', 'Off Campus Permission'),
        ]
    }
    return render(request, 'tokenization/create_permission_token.html', context)

def view_token(request, token_id):
    """View token details"""
    token = get_object_or_404(Token, id=token_id)
    comments = TokenComment.objects.filter(token=token).order_by('-created_at')
    
    context = {
        'token': token,
        'comments': comments,
        'teachers': Teacher.objects.all()[:10],  # For demo
    }
    return render(request, 'tokenization/view_token.html', context)

def update_token_status(request, token_id):
    """Update token status (for teachers/admin)"""
    token = get_object_or_404(Token, id=token_id)
    
    if request.method == 'POST':
        try:
            status = request.POST.get('status')
            rejection_reason = request.POST.get('rejection_reason', '')
            assigned_to_id = request.POST.get('assigned_to')
            
            token.status = status
            
            if status == TokenStatus.REJECTED:
                token.rejection_reason = rejection_reason
            
            if assigned_to_id:
                assigned_to = get_object_or_404(Teacher, id=assigned_to_id)
                token.assigned_to = assigned_to
            
            token.save()
            
            messages.success(request, f'Token #{token.token_number} status updated to {token.get_status_display()}')
            
        except Exception as e:
            messages.error(request, f'Error updating token: {str(e)}')
    
    return redirect('view_token', token_id=token.id)

def add_comment(request, token_id):
    """Add comment to token"""
    token = get_object_or_404(Token, id=token_id)
    
    if request.method == 'POST':
        try:
            comment_text = request.POST.get('comment')
            is_internal = request.POST.get('is_internal', False) == 'on'
            
            # For demo, use first teacher
            teacher = Teacher.objects.first()
            
            if not teacher:
                messages.error(request, "No teacher found to add comment")
                return redirect('view_token', token_id=token.id)
            
            TokenComment.objects.create(
                token=token,
                author=teacher,
                comment=comment_text,
                is_internal_note=is_internal
            )
            
            messages.success(request, 'Comment added successfully!')
            
        except Exception as e:
            messages.error(request, f'Error adding comment: {str(e)}')
    
    return redirect('view_token', token_id=token.id)

# ========== TEACHER/ADMIN VIEWS ==========

def teacher_dashboard(request):
    """Teacher dashboard"""
    # For demo, get first teacher
    teacher = Teacher.objects.first()
    
    if not teacher:
        messages.error(request, "No teacher found")
        return redirect('index')
    
    assigned_tokens = Token.objects.filter(assigned_to=teacher)
    all_tokens = Token.objects.all()
    
    context = {
        'teacher': teacher,
        'assigned_tokens': assigned_tokens,
        'total_assigned': assigned_tokens.count(),
        'pending_assigned': assigned_tokens.filter(status=TokenStatus.PENDING).count(),
        'all_tokens': all_tokens,
        'total_tokens': all_tokens.count(),
        'pending_tokens': all_tokens.filter(status=TokenStatus.PENDING).count(),
        'overdue_tokens': all_tokens.filter(status__in=[TokenStatus.PENDING, TokenStatus.PROCESSING], due_date__lt=date.today()).count(),
    }
    return render(request, 'tokenization/teacher_dashboard.html', context)

def all_tokens(request):
    """View all tokens"""
    tokens = Token.objects.all().order_by('-created_date')
    
    # Filtering
    token_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    batch_id = request.GET.get('batch', '')
    
    if token_type:
        tokens = tokens.filter(token_type=token_type)
    if status:
        tokens = tokens.filter(status=status)
    if priority:
        tokens = tokens.filter(priority=priority)
    if batch_id:
        tokens = tokens.filter(batch_id=batch_id)
    
    context = {
        'tokens': tokens,
        'token_types': TokenType.choices,
        'status_choices': TokenStatus.choices,
        'priority_choices': PriorityLevel.choices,
        'batches': Batch.objects.all(),
        'selected_type': token_type,
        'selected_status': status,
        'selected_priority': priority,
        'selected_batch': batch_id,
    }
    return render(request, 'tokenization/all_tokens.html', context)

def token_statistics(request):
    """Token statistics"""
    tokens = Token.objects.all()
    
    # Status distribution
    status_counts = {}
    for status_code, status_name in TokenStatus.choices:
        status_counts[status_name] = tokens.filter(status=status_code).count()
    
    # Type distribution
    type_counts = {}
    for type_code, type_name in TokenType.choices:
        type_counts[type_name] = tokens.filter(token_type=type_code).count()
    
    # Priority distribution
    priority_counts = {}
    for priority_code, priority_name in PriorityLevel.choices:
        priority_counts[priority_name] = tokens.filter(priority=priority_code).count()
    
    # Recent tokens
    recent_tokens = tokens.order_by('-created_date')[:10]
    
    # Overdue tokens
    overdue_tokens = tokens.filter(
        status__in=[TokenStatus.PENDING, TokenStatus.PROCESSING],
        due_date__lt=date.today()
    ).count()
    
    context = {
        'total_tokens': tokens.count(),
        'status_counts': status_counts,
        'type_counts': type_counts,
        'priority_counts': priority_counts,
        'recent_tokens': recent_tokens,
        'overdue_tokens': overdue_tokens,
        'students_with_tokens': Student.objects.filter(tokens__isnull=False).distinct().count(),
        'teachers_involved': Teacher.objects.filter(
            Q(assigned_tokens__isnull=False) | Q(approved_tokens__isnull=False)
        ).distinct().count(),
    }
    return render(request, 'tokenization/statistics.html', context)

# ========== API ENDPOINTS (for AJAX) ==========

def get_student_info(request, student_id):
    """Get student info for AJAX"""
    student = get_object_or_404(Student, id=student_id)
    
    data = {
        'id': student.id,
        'student_id': student.student_id,
        'name': student.full_name,
        'batch': student.batch.name,
        'semester': student.semester.number,
        'section': student.section.name,
        'discipline': student.discipline.name,
    }
    return JsonResponse(data)

def get_token_info(request, token_id):
    """Get token info for AJAX"""
    token = get_object_or_404(Token, id=token_id)
    
    data = {
        'id': token.id,
        'token_number': token.token_number,
        'student_name': token.student.full_name,
        'student_id': token.student.student_id,
        'token_type': token.get_token_type_display(),
        'status': token.get_status_display(),
        'title': token.title,
        'description': token.description,
        'created_date': token.created_date.strftime('%Y-%m-%d'),
        'due_date': token.due_date.strftime('%Y-%m-%d'),
        'is_overdue': token.is_overdue,
        'days_remaining': token.days_remaining,
    }
    return JsonResponse(data)

def search_tokens(request):
    """Search tokens"""
    query = request.GET.get('q', '')
    
    if not query:
        return JsonResponse({'tokens': []})
    
    tokens = Token.objects.filter(
        Q(token_number__icontains=query) |
        Q(title__icontains=query) |
        Q(student__student_id__icontains=query) |
        Q(student__first_name__icontains=query) |
        Q(student__last_name__icontains=query)
    )[:10]
    
    token_list = []
    for token in tokens:
        token_list.append({
            'id': token.id,
            'token_number': token.token_number,
            'title': token.title,
            'student_name': token.student.full_name,
            'status': token.get_status_display(),
            'created_date': token.created_date.strftime('%Y-%m-%d'),
        })
    
    return JsonResponse({'tokens': token_list})

# ========== DEMO DATA GENERATION ==========

def generate_demo_data(request):
    """Generate demo data for testing"""
    try:
        # Get first student and teacher
        student = Student.objects.first()
        teacher = Teacher.objects.first()
        
        if not student or not teacher:
            messages.error(request, "Need at least one student and one teacher in the system")
            return redirect('index')
        
        # Create sample tokens
        tokens_data = [
            {
                'title': 'Leave Request for Medical Checkup',
                'description': 'Need 2 days leave for medical appointment',
                'token_type': TokenType.PERMISSION,
                'priority': PriorityLevel.MEDIUM,
            },
            {
                'title': 'Attendance Correction - CS101',
                'description': 'I was present but marked absent on 2024-01-15',
                'token_type': TokenType.ATTENDANCE,
                'priority': PriorityLevel.HIGH,
            },
            {
                'title': 'Make-up Exam Request',
                'description': 'Missed final exam due to illness',
                'token_type': TokenType.EXAM,
                'priority': PriorityLevel.URGENT,
            },
            {
                'title': 'Library Book Extension',
                'description': 'Need 7 more days to complete research',
                'token_type': TokenType.LIBRARY,
                'priority': PriorityLevel.LOW,
            },
            {
                'title': 'Fee Payment Extension',
                'description': 'Requesting 15 days extension for semester fee',
                'token_type': TokenType.FEE,
                'priority': PriorityLevel.HIGH,
            },
        ]
        
        created_count = 0
        for i, token_data in enumerate(tokens_data):
            token = Token.objects.create(
                student=student,
                title=token_data['title'],
                description=token_data['description'],
                token_type=token_data['token_type'],
                priority=token_data['priority'],
                batch=student.batch,
                semester=student.semester,
                section=student.section,
                discipline=student.discipline,
                created_date=date.today() - timedelta(days=i),
                due_date=date.today() + timedelta(days=7-i),
                assigned_to=teacher if i % 2 == 0 else None,
                status=TokenStatus.PENDING if i < 3 else TokenStatus.APPROVED,
            )
            created_count += 1
        
        messages.success(request, f'Successfully created {created_count} demo tokens!')
        
    except Exception as e:
        messages.error(request, f'Error generating demo data: {str(e)}')
    
    return redirect('index')

# ========== ERROR PAGES ==========

def handler404(request, exception):
    """Custom 404 page"""
    return render(request, 'tokenization/404.html', status=404)

def handler500(request):
    """Custom 500 page"""
    return render(request, 'tokenization/500.html', status=500)
def token_dashboard(request):
    tokens = Token.objects.filter(student=request.user)

    context = {
        'my_tokens_count': tokens.count(),
        'pending_tokens': tokens.filter(status='pending').count(),
        'completed_tokens': tokens.filter(status='completed').count(),
        'recent_tokens': tokens.order_by('-created_at')[:5],
    }
    return render(request, 'tokenization/token_dashboard.html', context)
