from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from teachers.models import Teacher  
from student.models import Batch, Semester, Section  ,Discipline


class Subject(models.Model):
    SUBJECT_TYPE_CHOICES = [
        ('core', 'Core'),
        ('elective', 'Elective'),
        ('general', 'General'),
    ]

    SEMESTER_CHOICES = [
        (1, '1st Semester'),
        (2, '2nd Semester'),
        (3, '3rd Semester'),
        (4, '4th Semester'),
        (5, '5th Semester'),
        (6, '6th Semester'),
        (7, '7th Semester'),
        (8, '8th Semester'),
    ]

    name = models.CharField(
        max_length=20,
        verbose_name="Subject Name",
        help_text="Enter the full name of the subject"
    )

    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Subject Code",
        help_text="Short code for the subject (e.g., CS101)"
    )

    subject_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Subject ID",
        help_text="Unique identifier for the subject"
    )

    semester = models.PositiveSmallIntegerField(
        choices=SEMESTER_CHOICES,
        verbose_name="Semester",
        help_text="Select which semester this subject belongs to",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(8)
        ]
    )
    desciplain=models.ForeignKey(Discipline,on_delete=models.CASCADE)

    subject_type = models.CharField(
        max_length=10,
        choices=SUBJECT_TYPE_CHOICES,
        default='elective',
        verbose_name="Subject Type"
    )

    credit_hours = models.PositiveSmallIntegerField(
        default=6,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        verbose_name="Credit Hours",
        help_text="Number of credit hours for this subject"
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Optional description about the subject"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name} (Sem: {self.semester})"

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ['semester', 'code']
        unique_together = ['code', 'semester']


class SubjectAssign(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="assigned_subjects",
        verbose_name="Teacher",
        help_text="Select the teacher for this subject"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="assigned_teachers",
        verbose_name="Subject",
        help_text="Select the subject to assign"
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="subject_assignments",
        verbose_name="Batch",
        help_text="Select the batch for this assignment"
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="subject_assignments",
        verbose_name="Semester",
        help_text="Select the semester for this assignment"
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="subject_assignments",
        verbose_name="Section",
        help_text="Select the section for this assignment"
    )

    assigned_date = models.DateField(
        auto_now_add=True,
        verbose_name="Assigned Date"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Active SubjectAssign"
    )

    class Meta:
        verbose_name = " SubjectAssign"
        verbose_name_plural = "SubjectAssign "
        unique_together = ['teacher', 'subject', 'batch', 'semester', 'section']
        ordering = ['teacher', 'subject']

def __str__(self):
    discipline_name = self.subject.desciplain.name if self.subject.desciplain else "No Discipline"
    return f"{self.subject.code} - {self.subject.name} (Sem {self.subject.semester}) - {discipline_name}"
