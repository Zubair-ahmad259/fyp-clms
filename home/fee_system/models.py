from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from student.models import Batch, Semester, Section, Student,Discipline

class UploadFee(models.Model):
    SEMESTER_CHOICES = [(i, f"Semester {i}") for i in range(1, 9)]

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)
    due_date = models.DateField(null=True, blank=True)

    semester_option = models.IntegerField(
        choices=SEMESTER_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        help_text="Select the semester this fee applies to"
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00  # Add this default value
    )
    fine = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Enter any fine amount (default is 5000)"
    )
    upload_date = models.DateField(auto_now_add=True)

    # ... rest of the model ...
    class Meta:
        ordering = ['batch', 'semester', 'section', 'student']
        unique_together = ('student', 'semester_option')

    def total_fee(self):
        """Return fee + fine"""
        return self.amount + self.fine

    def __str__(self):
        return f"Fee for {self.student} - Sem {self.semester_option} - Total: {self.total_fee()}"


class ClearFee(models.Model):
    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Online', 'Online Payment'),
    ]
    collector_name=[
        ('name1','name1'),
        ('name2','name2'),
        ('name3','name3'),

    ]

    upload_fee = models.OneToOneField(
        UploadFee,
        on_delete=models.CASCADE,
        related_name="clear_record"
    )
    receipt_number = models.CharField(max_length=50, unique=True)  # 🔹 unique receipt number
    cleared_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='Cash')
    collector_name = models.CharField(max_length=50,choices=collector_name,default=None)  
    cleared_date = models.DateField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['cleared_date']

    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.upload_fee.student} - {self.payment_method}"
