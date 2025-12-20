from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from student.models import Batch, Semester, Section, Student, Discipline
from decimal import Decimal

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
        default=0.00
    )
    fine = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Enter any fine amount (default is 5000)"
    )
    upload_date = models.DateField(auto_now_add=True)
    
    # Add payment status field
    is_fully_paid = models.BooleanField(default=False)
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total amount paid so far"
    )
    remaining_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Remaining amount to be paid"
    )

    class Meta:
        ordering = ['batch', 'semester', 'section', 'student']
        unique_together = ('student', 'semester_option')

    def save(self, *args, **kwargs):
        """Calculate remaining amount automatically"""
        # Ensure paid_amount is Decimal
        if not isinstance(self.paid_amount, Decimal):
            try:
                self.paid_amount = Decimal(str(self.paid_amount))
            except:
                self.paid_amount = Decimal('0.00')
        
        # Calculate remaining amount
        self.remaining_amount = self.total_fee() - self.paid_amount
        
        # Check if fully paid
        self.is_fully_paid = self.remaining_amount <= Decimal('0.00')
        
        super().save(*args, **kwargs)

    def total_fee(self):
        """Return fee + fine"""
        # Ensure both are Decimal
        amount = self.amount if isinstance(self.amount, Decimal) else Decimal(str(self.amount))
        fine = self.fine if isinstance(self.fine, Decimal) else Decimal(str(self.fine))
        return amount + fine

    def __str__(self):
        return f"Fee for {self.student} - Sem {self.semester_option} - Total: {self.total_fee()}"


class ClearFee(models.Model):
    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Online', 'Online Payment'),
    ]
    COLLECTOR_NAMES = [
        ('name1', 'name1'),
        ('name2', 'name2'),
        ('name3', 'name3'),
    ]

    # Changed from OneToOneField to ForeignKey
    upload_fee = models.ForeignKey(
        UploadFee,
        on_delete=models.CASCADE,
        related_name="clear_records"  # Changed to plural
    )
    receipt_number = models.CharField(max_length=50, blank=True)  # Made blank=True
    cleared_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='Cash')
    collector_name = models.CharField(max_length=50, choices=COLLECTOR_NAMES, default=None)  
    cleared_date = models.DateField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    
    # Add installment number for tracking multiple payments
    installment_number = models.PositiveIntegerField(
        default=1,
        help_text="Installment number for this payment"
    )

    class Meta:
        ordering = ['cleared_date']
        # Allow multiple receipts for the same upload_fee but different installments
        unique_together = ('upload_fee', 'installment_number')

    def save(self, *args, **kwargs):
        """Update parent UploadFee when payment is saved"""
        is_new = self.pk is None
        
        # Ensure cleared_amount is Decimal
        if not isinstance(self.cleared_amount, Decimal):
            self.cleared_amount = Decimal(str(self.cleared_amount))
        
        # If this is a new payment, calculate the next installment number
        if is_new:
            # Get the highest installment number for this upload_fee
            last_payment = ClearFee.objects.filter(
                upload_fee=self.upload_fee
            ).order_by('-installment_number').first()
            
            if last_payment:
                self.installment_number = last_payment.installment_number + 1
            else:
                self.installment_number = 1
        
        # Generate receipt number if not provided
        if is_new and not self.receipt_number:
            self.receipt_number = f"RCPT-{self.upload_fee.student.student_id}-{self.installment_number}"
        
        super().save(*args, **kwargs)
        
        # Update parent UploadFee's paid amount
        if is_new:
            upload_fee = self.upload_fee
            # Get all payments for this upload_fee
            all_payments = ClearFee.objects.filter(upload_fee=upload_fee)
            total_paid = sum(p.cleared_amount for p in all_payments)
            
            # Convert to Decimal if needed
            if not isinstance(total_paid, Decimal):
                total_paid = Decimal(str(total_paid))
            
            upload_fee.paid_amount = total_paid
            upload_fee.save()

    def delete(self, *args, **kwargs):
        """Update parent UploadFee when payment is deleted"""
        upload_fee = self.upload_fee
        
        super().delete(*args, **kwargs)
        
        # Recalculate paid amount
        all_payments = ClearFee.objects.filter(upload_fee=upload_fee)
        total_paid = sum(p.cleared_amount for p in all_payments)
        
        # Convert to Decimal if needed
        if not isinstance(total_paid, Decimal):
            total_paid = Decimal(str(total_paid))
        
        upload_fee.paid_amount = total_paid
        upload_fee.save()

    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.upload_fee.student} - Installment {self.installment_number}"