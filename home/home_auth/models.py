from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.db import models
from home import settings
# from student.models import Student,Batch,Semester,Section

class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_authorized = models.BooleanField(default=False)
    login_token = models.CharField(max_length=6, blank=True, null=True)
    is_student = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    password_change_deadline = models.DateTimeField(blank=True, null=True)
    password_generated = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Generate and send password only when creating user
        if not self.pk and not self.password_generated:
            random_password = get_random_string(length=10)
            self.set_password(random_password)
            self.password_generated = True
            self.password_change_deadline = timezone.now() + timedelta(hours=24)
            super().save(*args, **kwargs)
            self.send_password_email(random_password)
        else:
            super().save(*args, **kwargs)

    def send_password_email(self, password):
        subject = "Your Account Password"
        message = (
            f"Dear {self.first_name},\n\n"
        f"Welcome to the Learning Management System.\n\n"
        f"Your account has been successfully created.\n\n"
        f"Login Details:\n"
        f"Username: {self.username}\n"
        f"Temporary Password: {password}\n\n"
        f"For security reasons, please log in and change your password within 24 hours.\n"
        f"After 24 hours, password change will be locked.\n\n"
        f"Thank you for joining us.\n"
        f"Best regards,\n"
        f"LMS Administration Team"
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email], fail_silently=False)

    def can_change_password(self):
        return timezone.now() <= self.password_change_deadline

    def __str__(self):
        return self.username


class PasswordResetRequest(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.CharField(
        max_length=32,
        default=get_random_string, 
        editable=False,
        unique=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Define token validity period (e.g., 1 hour)
    TOKEN_VALIDITY_PERIOD = timezone.timedelta(hours=1)

    def is_valid(self):
        return timezone.now() <= self.created_at + self.TOKEN_VALIDITY_PERIOD

    def send_reset_email(self):
        reset_link = f"http://localhost:8000/authentication/reset-password/{self.token}/"
        send_mail(
            'Password Reset Request',
            f'Click the following link to reset your password: {reset_link}',
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )
 