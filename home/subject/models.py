from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from teachers.models import Teacher  
from Academic.models import Batch, Semester, Section, Discipline


class Subject(models.Model):
    # Simplified SUBJECT_TYPE_CHOICES
    SUBJECT_TYPE_CHOICES = [
        ('core', 'Core'),
        ('elective', 'Elective'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="Subject Name",
        help_text="Enter the full name of the subject"
    )

    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Subject Code",
        help_text="Short code for the subject (e.g., CS101)"
    )

    # CHANGED: IntegerField to ForeignKey to Semester model
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='subjects',
        verbose_name="Semester",
        help_text="Select which semester this subject belongs to"
    )
    
    # NEW: Section field added
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='subjects',
        verbose_name="Section",
        help_text="Select the section for this subject",
        null=True,
        blank=True  # Make it optional
    )
    
    desciplain = models.ForeignKey(
        Discipline, 
        on_delete=models.CASCADE, 
        related_name='subjects',
        verbose_name="Discipline"
    )
    
    # Simplified subject_type choices
    subject_type = models.CharField(
        max_length=10,
        choices=SUBJECT_TYPE_CHOICES,
        default='core',
        verbose_name="Subject Type"
    )

    # Prerequisite Subjects Field
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        verbose_name="Prerequisite Subjects",
        help_text="Select subjects that must be completed before taking this subject",
        related_name='is_prerequisite_for'
    )

    credit_hours = models.PositiveSmallIntegerField(
        default=3,
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
        section_str = f" - {self.section.name}" if self.section else ""
        return f"{self.code} - {self.name} (Sem {self.semester.number}{section_str})"

    # Method to check if student has completed prerequisites
    def check_prerequisites(self, student):
        """Check if student has passed all prerequisite subjects"""
        from student.models import StudentGrade
        
        # Get all prerequisite subjects
        prereqs = self.prerequisites.all()
        
        if not prereqs:
            return {
                'status': True,
                'message': 'No prerequisites required',
                'missing': []
            }
        
        missing_prereqs = []
        
        for prereq in prereqs:
            # Check if student has passed this prerequisite subject
            try:
                grade = StudentGrade.objects.get(
                    student=student,
                    subject=prereq
                )
                # Assuming StudentGrade has is_passed() method
                if hasattr(grade, 'is_passed') and not grade.is_passed():
                    missing_prereqs.append({
                        'subject': prereq,
                        'reason': f'Failed in {prereq.code}'
                    })
                elif grade.grade and grade.grade < 40:  # Simple check if grade < 40
                    missing_prereqs.append({
                        'subject': prereq,
                        'reason': f'Failed in {prereq.code} (Grade: {grade.grade})'
                    })
            except StudentGrade.DoesNotExist:
                missing_prereqs.append({
                    'subject': prereq,
                    'reason': f'Not enrolled in {prereq.code}'
                })
        
        if missing_prereqs:
            return {
                'status': False,
                'message': f'Missing {len(missing_prereqs)} prerequisite(s)',
                'missing': missing_prereqs
            }
        
        return {
            'status': True,
            'message': 'All prerequisites completed',
            'missing': []
        }

    # Get prerequisite chain
    def get_prerequisite_chain(self):
        """Get all prerequisite subjects recursively"""
        def get_prereqs(subject, chain=None):
            if chain is None:
                chain = []
            
            prereqs = subject.prerequisites.all()
            for prereq in prereqs:
                if prereq not in chain:
                    chain.append(prereq)
                    get_prereqs(prereq, chain)
            
            return chain
        
        return get_prereqs(self)

    # Simple property to display prerequisites
    @property
    def prerequisite_codes(self):
        return ", ".join([p.code for p in self.prerequisites.all()]) or "None"

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ['semester__number', 'code']
        unique_together = ['code', 'semester', 'desciplain', 'section']


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
    
    discipline = models.ForeignKey(
        Discipline, 
        on_delete=models.CASCADE,
        verbose_name="Discipline"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Active SubjectAssign"
    )

    class Meta:
        verbose_name = "Subject Assignment"
        verbose_name_plural = "Subject Assignments"
        unique_together = ['teacher', 'subject', 'batch', 'semester', 'section']
        ordering = ['teacher', 'subject']

    def __str__(self):
        discipline_name = self.subject.desciplain.name if self.subject.desciplain else "No Discipline"
        return f"{self.subject.code} - {self.subject.name} (Sem {self.subject.semester.number}) - {discipline_name}"