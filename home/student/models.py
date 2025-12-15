from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from home_auth.models import CustomUser

    
 
class Discipline(models.Model):
    PROGRAM_CHOICES = [
        ('BS', 'BS'),
        ('MS', 'MS'),
        ('PhD', 'PhD'),
    ]

    FIELD_CHOICES = [
        ('Computer Science', 'Computer Science'),
        ('Software Engineering', 'Software Engineering'),
        ('ARTIFICIAL INTELLIGENCE', 'ARTIFICIAL INTELLIGENCE'),
        ('CYBER SECURITY', 'CYBER SECURITY'),
        ('DATA SCIENCE', 'DATA SCIENCE'),


    ]

    program = models.CharField(max_length=10, choices=PROGRAM_CHOICES)
    field = models.CharField(max_length=50, choices=FIELD_CHOICES)

    class Meta:
        unique_together = ('program', 'field')
        verbose_name = "Discipline"
        verbose_name_plural = "Disciplines"

    def __str__(self):
        return f"{self.program} in {self.field}"



class Batch(models.Model):
    name = models.CharField(max_length=50, unique=False)
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)  


    def __str__(self):
        return self.name

class Semester(models.Model):
    number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        unique=True
    )
    description = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Semester {self.number}"

class Section(models.Model):
    name = models.CharField(max_length=10, unique=False)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ('name', 'batch')  # Ensures unique section names per batch

    def __str__(self):
        if self.batch:
            return f"{self.name} ({self.batch.name})"
        return self.name

class Parent(models.Model):
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    father_email = models.EmailField(blank=True, null=True)
    father_contact = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField()

    def __str__(self):
        return f"{self.father_name}"
    

class Student(models.Model):

    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    # Basic Info
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    student_id = models.CharField(max_length=20, unique=True)
    admission_number = models.CharField(max_length=20, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    dob = models.DateField()
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=15, blank=True)

    image = models.ImageField(upload_to='students/', blank=True, null=True)

    # Academic Info
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)  

    

    parent = models.OneToOneField(Parent, on_delete=models.CASCADE, related_name='student', null=True, blank=True)    # Additional Info
    address = models.TextField()

    class Meta:
        ordering = ['batch', 'section', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"
    



