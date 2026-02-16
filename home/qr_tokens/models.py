# tokenization/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date, timedelta
from django.conf import settings
from student.models import Student, Batch, Semester, Section, Discipline
from teachers.models import Teacher
from subject.models import Subject
from attendance.models import AttendanceStatus
from exam_mang.models import Exam, SubjectMarkComponents

class TokenType(models.TextChoices):
    PERMISSION = 'PERMISSION', 'Permission'
    MAKEUP = 'MAKEUP', 'Make-up'
    ATTENDANCE = 'ATTENDANCE', 'Attendance Correction'
    EXAM = 'EXAM', 'Exam Token'
    FEE = 'FEE', 'Fee Extension'
    LIBRARY = 'LIBRARY', 'Library'
    OTHER = 'OTHER', 'Other'

class TokenStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    CANCELLED = 'CANCELLED', 'Cancelled'
    PROCESSING = 'PROCESSING', 'Processing'
    COMPLETED = 'COMPLETED', 'Completed'

class PriorityLevel(models.TextChoices):
    LOW = 'LOW', 'Low'
    MEDIUM = 'MEDIUM', 'Medium'
    HIGH = 'HIGH', 'High'
    URGENT = 'URGENT', 'Urgent'

class Token(models.Model):
    # Basic Information
    token_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Token Number"
    )
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='tokens',
        verbose_name="Student"
    )
    
    token_type = models.CharField(
        max_length=20,
        choices=TokenType.choices,
        verbose_name="Token Type"
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name="Token Title"
    )
    
    description = models.TextField(
        verbose_name="Description",
        help_text="Detailed description of the token request"
    )
    
    # Status and Priority
    status = models.CharField(
        max_length=20,
        choices=TokenStatus.choices,
        default=TokenStatus.PENDING,
        verbose_name="Status"
    )
    
    priority = models.CharField(
        max_length=20,
        choices=PriorityLevel.choices,
        default=PriorityLevel.MEDIUM,
        verbose_name="Priority Level"
    )
    
    # Academic Information
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name='tokens',
        verbose_name="Batch"
    )
    
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='tokens',
        verbose_name="Semester"
    )
    
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='tokens',
        verbose_name="Section"
    )
    
    discipline = models.ForeignKey(
        Discipline,
        on_delete=models.CASCADE,
        related_name='tokens',
        verbose_name="Discipline"
    )
    
    # Dates
    created_date = models.DateField(
        default=date.today,
        verbose_name="Created Date"
    )
    
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Submitted At"
    )
    
    due_date = models.DateField(
        verbose_name="Due Date",
        help_text="Date by which this token should be processed"
    )
    
    resolved_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Resolved Date"
    )
    
    # Processing Information
    assigned_to = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        related_name='assigned_tokens',
        null=True,
        blank=True,
        verbose_name="Assigned To"
    )
    
    approved_by = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        related_name='approved_tokens',
        null=True,
        blank=True,
        verbose_name="Approved By"
    )
    
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name="Rejection Reason",
        help_text="Reason for rejecting the token"
    )
    
    # Additional Fields
    attachment = models.FileField(
        upload_to='token_attachments/',
        blank=True,
        null=True,
        verbose_name="Attachment",
        help_text="Upload supporting documents if any"
    )
    
    is_urgent = models.BooleanField(
        default=False,
        verbose_name="Urgent Request"
    )
    
    requires_parent_approval = models.BooleanField(
        default=False,
        verbose_name="Requires Parent Approval"
    )
    
    parent_approved = models.BooleanField(
        default=False,
        verbose_name="Parent Approved"
    )
    
    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Token"
        verbose_name_plural = "Tokens"
        ordering = ['-submitted_at', 'priority']
        indexes = [
            models.Index(fields=['token_number']),
            models.Index(fields=['student', 'status']),
            models.Index(fields=['token_type', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]

    def __str__(self):
        return f"{self.token_number} - {self.student.student_id} - {self.get_token_type_display()}"

    def save(self, *args, **kwargs):
        # Generate token number if not provided
        if not self.token_number:
            year = timezone.now().strftime('%Y')
            token_count = Token.objects.filter(created_date__year=timezone.now().year).count() + 1
            self.token_number = f"TK-{year}-{token_count:05d}"
        
        # Auto-fill academic information from student if not provided
        if not self.batch_id and self.student_id:
            self.batch = self.student.batch
        if not self.semester_id and self.student_id:
            self.semester = self.student.semester
        if not self.section_id and self.student_id:
            self.section = self.student.section
        if not self.discipline_id and self.student_id:
            self.discipline = self.student.discipline
        
        # Set due date if not provided (default 7 days from creation)
        if not self.due_date:
            self.due_date = self.created_date + timedelta(days=7)
        
        # Set resolved_date if status is COMPLETED or REJECTED
        if self.status in [TokenStatus.COMPLETED, TokenStatus.REJECTED] and not self.resolved_date:
            self.resolved_date = date.today()
        
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if token is overdue"""
        return date.today() > self.due_date and self.status not in [TokenStatus.COMPLETED, TokenStatus.REJECTED, TokenStatus.CANCELLED]

    @property
    def days_remaining(self):
        """Calculate days remaining until due date"""
        if self.status in [TokenStatus.COMPLETED, TokenStatus.REJECTED, TokenStatus.CANCELLED]:
            return 0
        remaining = (self.due_date - date.today()).days
        return max(0, remaining)

    @property
    def is_high_priority(self):
        """Check if token is high priority"""
        return self.priority in [PriorityLevel.HIGH, PriorityLevel.URGENT] or self.is_urgent

class AttendanceToken(Token):
    """Token for attendance-related requests"""
    attendance_date = models.DateField(
        verbose_name="Attendance Date"
    )
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='attendance_tokens',
        verbose_name="Subject"
    )
    
    original_status = models.CharField(
        max_length=1,
        choices=AttendanceStatus.choices,
        verbose_name="Original Status",
        help_text="Original attendance status"
    )
    
    requested_status = models.CharField(
        max_length=1,
        choices=AttendanceStatus.choices,
        verbose_name="Requested Status",
        help_text="Requested attendance status"
    )
    
    reason_for_change = models.TextField(
        verbose_name="Reason for Change",
        help_text="Reason for requesting attendance status change"
    )
    
    supporting_evidence = models.TextField(
        blank=True,
        null=True,
        verbose_name="Supporting Evidence",
        help_text="Any supporting evidence for the request"
    )
    
    # Reference to specific attendance record if applicable
    attendance_record = models.ForeignKey(
        'attendance.Attendance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Attendance Record"
    )

    class Meta:
        verbose_name = "Attendance Token"
        verbose_name_plural = "Attendance Tokens"

    def save(self, *args, **kwargs):
        # Set token type automatically
        self.token_type = TokenType.ATTENDANCE
        super().save(*args, **kwargs)

    @property
    def attendance_percentage_impact(self):
        """Calculate the impact on attendance percentage if approved"""
        # This would calculate how much the attendance percentage would change
        # Implementation depends on your attendance calculation logic
        return 0

class ExamToken(Token):
    """Token for exam-related requests"""
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='tokens',
        verbose_name="Exam"
    )
    
    subject_mark_component = models.ForeignKey(
        SubjectMarkComponents,
        on_delete=models.CASCADE,
        related_name='exam_tokens',
        verbose_name="Subject Mark Component"
    )
    
    request_type = models.CharField(
        max_length=50,
        choices=[
            ('MAKEUP_EXAM', 'Make-up Exam'),
            ('EXAM_RESCHEDULE', 'Exam Reschedule'),
            ('SPECIAL_ASSISTANCE', 'Special Assistance'),
            ('OTHER_EXAM_REQUEST', 'Other Exam Request'),
        ],
        verbose_name="Request Type"
    )
    
    requested_exam_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Requested Exam Date"
    )
    
    medical_certificate = models.FileField(
        upload_to='medical_certificates/',
        blank=True,
        null=True,
        verbose_name="Medical Certificate"
    )
    
    previous_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name="Previous Attempts"
    )
    
    is_medical_case = models.BooleanField(
        default=False,
        verbose_name="Medical Case"
    )
    
    doctor_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Doctor's Notes"
    )

    class Meta:
        verbose_name = "Exam Token"
        verbose_name_plural = "Exam Tokens"

    def save(self, *args, **kwargs):
        # Set token type automatically
        self.token_type = TokenType.EXAM
        super().save(*args, **kwargs)

class PermissionToken(Token):
    """Token for permission requests"""
    PERMISSION_TYPES = [
        ('LEAVE', 'Leave Request'),
        ('LATE_ENTRY', 'Late Entry'),
        ('EARLY_EXIT', 'Early Exit'),
        ('SPECIAL_PERMISSION', 'Special Permission'),
        ('OFF_CAMPUS', 'Off Campus Permission'),
    ]
    
    permission_type = models.CharField(
        max_length=50,
        choices=PERMISSION_TYPES,
        verbose_name="Permission Type"
    )
    
    start_date = models.DateField(
        verbose_name="Start Date"
    )
    
    end_date = models.DateField(
        verbose_name="End Date"
    )
    
    start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Start Time"
    )
    
    end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="End Time"
    )
    
    reason_for_permission = models.TextField(
        verbose_name="Reason for Permission"
    )
    
    emergency_contact = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Emergency Contact"
    )
    
    emergency_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Emergency Phone"
    )
    
    destination = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Destination"
    )
    
    guardian_approval = models.BooleanField(
        default=False,
        verbose_name="Guardian Approval"
    )

    class Meta:
        verbose_name = "Permission Token"
        verbose_name_plural = "Permission Tokens"

    def save(self, *args, **kwargs):
        # Set token type automatically
        self.token_type = TokenType.PERMISSION
        super().save(*args, **kwargs)

    @property
    def duration_days(self):
        """Calculate duration in days"""
        return (self.end_date - self.start_date).days + 1

class TokenComment(models.Model):
    """Comments/notes on tokens"""
    token = models.ForeignKey(
        Token,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Token"
    )
    
    author = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='token_comments',
        verbose_name="Author"
    )
    
    comment = models.TextField(
        verbose_name="Comment"
    )
    
    is_internal_note = models.BooleanField(
        default=False,
        verbose_name="Internal Note",
        help_text="If True, comment is not visible to student"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Token Comment"
        verbose_name_plural = "Token Comments"
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment on {self.token.token_number} by {self.author.name}"

class TokenWorkflow(models.Model):
    """Workflow tracking for token processing"""
    token = models.ForeignKey(
        Token,
        on_delete=models.CASCADE,
        related_name='workflow_steps',
        verbose_name="Token"
    )
    
    step_name = models.CharField(
        max_length=100,
        verbose_name="Step Name"
    )
    
    assigned_to = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workflow_tasks',
        verbose_name="Assigned To"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('SKIPPED', 'Skipped'),
        ],
        default='PENDING',
        verbose_name="Step Status"
    )
    
    completed_by = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_workflow_tasks',
        verbose_name="Completed By"
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Completed At"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Step Notes"
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Step Order"
    )
    
    is_required = models.BooleanField(
        default=True,
        verbose_name="Required Step"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Token Workflow Step"
        verbose_name_plural = "Token Workflow Steps"
        ordering = ['order']
        unique_together = ['token', 'step_name']

    def __str__(self):
        return f"{self.token.token_number} - {self.step_name}"

class TokenNotification(models.Model):
    """Notifications for token updates"""
    NOTIFICATION_TYPES = [
        ('STATUS_CHANGE', 'Status Change'),
        ('ASSIGNMENT', 'Assignment'),
        ('COMMENT', 'Comment'),
        ('OVERDUE', 'Overdue'),
        ('REMINDER', 'Reminder'),
    ]
    
    token = models.ForeignKey(
        Token,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Token"
    )
    
    recipient = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='token_notifications',
        verbose_name="Recipient"
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        verbose_name="Notification Type"
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name="Notification Title"
    )
    
    message = models.TextField(
        verbose_name="Notification Message"
    )
    
    is_read = models.BooleanField(
        default=False,
        verbose_name="Is Read"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Token Notification"
        verbose_name_plural = "Token Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.student_id} - {self.notification_type} - {self.created_at.date()}"

class TokenCategory(models.Model):
    """Categories for organizing tokens"""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Category Name"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description"
    )
    
    default_priority = models.CharField(
        max_length=20,
        choices=PriorityLevel.choices,
        default=PriorityLevel.MEDIUM,
        verbose_name="Default Priority"
    )
    
    sla_days = models.PositiveIntegerField(
        default=7,
        verbose_name="SLA Days",
        help_text="Service Level Agreement - Days to resolve"
    )
    
    requires_approval = models.BooleanField(
        default=True,
        verbose_name="Requires Approval"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Token Category"
        verbose_name_plural = "Token Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class TokenRule(models.Model):
    """Business rules for token processing"""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Rule Name"
    )
    
    description = models.TextField(
        verbose_name="Rule Description"
    )
    
    condition = models.TextField(
        verbose_name="Condition",
        help_text="Python condition to evaluate (returns True/False)"
    )
    
    action = models.TextField(
        verbose_name="Action",
        help_text="Python code to execute if condition is True"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active"
    )
    
    priority = models.PositiveIntegerField(
        default=0,
        verbose_name="Priority",
        help_text="Higher number = higher priority"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Token Rule"
        verbose_name_plural = "Token Rules"
        ordering = ['-priority', 'name']

    def __str__(self):
        return self.name

class TokenStatistics(models.Model):
    """Statistics for token processing"""
    date = models.DateField(
        unique=True,
        verbose_name="Date"
    )
    
    total_tokens = models.PositiveIntegerField(
        default=0,
        verbose_name="Total Tokens"
    )
    
    pending_tokens = models.PositiveIntegerField(
        default=0,
        verbose_name="Pending Tokens"
    )
    
    resolved_tokens = models.PositiveIntegerField(
        default=0,
        verbose_name="Resolved Tokens"
    )
    
    overdue_tokens = models.PositiveIntegerField(
        default=0,
        verbose_name="Overdue Tokens"
    )
    
    avg_resolution_time = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Average Resolution Time (hours)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Token Statistics"
        verbose_name_plural = "Token Statistics"
        ordering = ['-date']

    def __str__(self):
        return f"Token Stats - {self.date}"

    def calculate_statistics(self):
        """Calculate statistics for the date"""
        from django.db.models import Avg, Count, Q
        
        tokens = Token.objects.filter(created_date=self.date)
        
        self.total_tokens = tokens.count()
        self.pending_tokens = tokens.filter(status=TokenStatus.PENDING).count()
        self.resolved_tokens = tokens.filter(status__in=[TokenStatus.COMPLETED, TokenStatus.REJECTED]).count()
        self.overdue_tokens = tokens.filter(status__in=[TokenStatus.PENDING, TokenStatus.PROCESSING], due_date__lt=self.date).count()
        
        # Calculate average resolution time
        resolved_tokens = tokens.filter(resolved_date=self.date)
        if resolved_tokens.exists():
            # Calculate hours between created and resolved
            # This is simplified - you might want to implement a more precise calculation
            self.avg_resolution_time = 24.0  # Placeholder
        
        self.save()