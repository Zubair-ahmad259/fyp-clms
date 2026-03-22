from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from teachers.models import Teacher
from subject.models import Subject, SubjectAssign
from Academic.models import Batch, Semester, Section, Discipline

class Room(models.Model):
    """Classroom or Lab where classes are held"""
    ROOM_TYPES = [
        ('classroom', 'Classroom'),
        ('lab', 'Laboratory'),
        ('auditorium', 'Auditorium'),
        ('seminar', 'Seminar Hall'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    room_number = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='classroom')
    building = models.CharField(max_length=100, blank=True)
    floor = models.IntegerField(default=0)
    has_projector = models.BooleanField(default=False)
    has_whiteboard = models.BooleanField(default=True)
    has_ac = models.BooleanField(default=False)
    is_lab = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.room_number}) - Cap: {self.capacity}"
    
    class Meta:
        ordering = ['building', 'floor', 'name']


class TimeSlot(models.Model):
    """Defines time slots for classes"""
    DAYS_OF_WEEK = [
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        (7, 'Sunday'),
    ]
    
    day = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_number = models.IntegerField(help_text="Order of slot in the day (1,2,3...)")
    
    class Meta:
        unique_together = ['day', 'start_time', 'end_time']
        ordering = ['day', 'start_time']
    
    def __str__(self):
        day_name = dict(self.DAYS_OF_WEEK)[self.day]
        return f"{day_name} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
    
    @property
    def duration_hours(self):
        """Calculate duration in hours"""
        delta = datetime.combine(date.today(), self.end_time) - datetime.combine(date.today(), self.start_time)
        return delta.total_seconds() / 3600
class Timetable(models.Model):
    """Main Timetable model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=200)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, related_name='timetables')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='timetables')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='timetables')
    academic_year = models.CharField(max_length=20, help_text="e.g., 2024-2025")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='timetables')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.discipline} - Batch {self.batch} - Sem {self.semester.number}"
    
    class Meta:
        unique_together = ['discipline', 'batch', 'semester', 'academic_year']

class TimetableEntry(models.Model):
    """Individual class entry in the timetable"""
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='entries')
    subject_assign = models.ForeignKey(SubjectAssign, on_delete=models.CASCADE, related_name='timetable_entries')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='timetable_entries')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetable_entries')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='timetable_entries')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='timetable_entries')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='timetable_entries')
    
    # For recurring entries
    WEEK_TYPES = [
        ('every', 'Every Week'),
        ('odd', 'Odd Weeks'),
        ('even', 'Even Weeks'),
        ('alternate', 'Alternate Weeks'),
        ('once', 'Once'),
    ]
    
    week_type = models.CharField(max_length=20, choices=WEEK_TYPES, default='every')
    start_week = models.IntegerField(default=1, help_text="Starting week number (1-16)")
    end_week = models.IntegerField(default=16, help_text="Ending week number (1-16)")
    
    # For specific date exceptions
    is_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True)
    replaced_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replacements')
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.subject.code} - {self.teacher} - {self.time_slot}"
    
    class Meta:
        verbose_name_plural = "Timetable Entries"
        ordering = ['time_slot__day', 'time_slot__start_time']
        unique_together = ['timetable', 'teacher', 'time_slot', 'section']  # Prevent double booking


class TeacherAvailability(models.Model):
    """Teacher's availability for classes"""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='availabilities')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    reason = models.CharField(max_length=200, blank=True)
    
    class Meta:
        unique_together = ['teacher', 'time_slot', 'semester']
    
    def __str__(self):
        status = "Available" if self.is_available else "Unavailable"
        return f"{self.teacher} - {self.time_slot} - {status}"


class RoomAvailability(models.Model):
    """Room availability for classes"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='availabilities')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    reason = models.CharField(max_length=200, blank=True)
    
    class Meta:
        unique_together = ['room', 'time_slot', 'semester']
    
    def __str__(self):
        status = "Available" if self.is_available else "Unavailable"
        return f"{self.room} - {self.time_slot} - {status}"


class TimetableConstraint(models.Model):
    """Constraints for automatic timetable generation"""
    CONSTRAINT_TYPES = [
        ('no_overlap_teacher', 'No Teacher Overlap'),
        ('no_overlap_room', 'No Room Overlap'),
        ('no_overlap_section', 'No Section Overlap'),
        ('teacher_max_hours', 'Teacher Max Hours'),
        ('subject_consecutive', 'Subject Consecutive Limit'),
        ('preferred_time', 'Preferred Time'),
        ('avoid_time', 'Avoid Time'),
    ]
    
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='constraints')
    constraint_type = models.CharField(max_length=30, choices=CONSTRAINT_TYPES)
    
    # For teacher-specific constraints
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    
    # For subject-specific constraints
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    
    # For time-specific constraints
    day = models.IntegerField(choices=TimeSlot.DAYS_OF_WEEK, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    
    # Value for constraints (e.g., max hours per day)
    value = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=1, help_text="Higher number = higher priority")
    
    def __str__(self):
        return f"{self.get_constraint_type_display()} - {self.timetable}"


class GeneratedTimetable(models.Model):
    """Store generated timetable versions"""
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='generations')
    generation_date = models.DateTimeField(auto_now_add=True)
    algorithm_used = models.CharField(max_length=50, default='genetic')
    fitness_score = models.FloatField(default=0)
    is_selected = models.BooleanField(default=False)
    generation_data = models.JSONField(help_text="Store the complete timetable data as JSON")
    stats = models.JSONField(default=dict, help_text="Generation statistics")
    
    def __str__(self):
        return f"{self.timetable} - Generated on {self.generation_date}"


class TimetableConflict(models.Model):
    """Track conflicts in timetable"""
    SEVERITY_LEVELS = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('warning', 'Warning'),
    ]
    
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='conflicts')
    entry1 = models.ForeignKey(TimetableEntry, on_delete=models.CASCADE, related_name='conflicts_as_first')
    entry2 = models.ForeignKey(TimetableEntry, on_delete=models.CASCADE, related_name='conflicts_as_second', null=True, blank=True)
    conflict_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Conflict in {self.timetable}: {self.conflict_type}"