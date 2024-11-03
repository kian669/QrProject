from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

from django.utils import timezone

class User(AbstractUser):
    # Additional fields for your custom user model
    user_type = models.CharField(max_length=20, choices=[('security', 'Security'), ('student', 'Student'), ('head', 'Head of Security')])

    # Add related_name to avoid conflict with Django's default User model
    groups = models.ManyToManyField(
        Group,
        related_name='qrapp_user_groups',  # Unique related name
        blank=True,
        help_text="The groups this user belongs to."
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='qrapp_user_permissions',  # Unique related name
        blank=True,
        help_text="Specific permissions for this user."
    )

    def __str__(self):
        return f"{self.username} ({self.user_type})"


class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    course = models.CharField(max_length=100)
    year = models.CharField(max_length=10)
    major = models.CharField(max_length=100)
    or_upload = models.FileField(upload_to='uploads/or/')
    cr_upload = models.FileField(upload_to='uploads/cr/')
    license_upload = models.FileField(upload_to='uploads/license/')
    password = models.CharField(max_length=128, blank=True, null=False)


    def __str__(self):
        return f"{self.username} ({self.student_id})"
    
class StudentMasterList(models.Model):
        student_id = models.CharField(max_length=20, unique=True)
        username = models.CharField(max_length=50)
        email = models.EmailField(unique=True)
        first_name = models.CharField(max_length=50, blank=True, null=True)
        last_name = models.CharField(max_length=50, blank=True, null=True)
        course = models.CharField(max_length=100)
        year = models.CharField(max_length=10)
        major = models.CharField(max_length=100)
        or_upload = models.FileField(upload_to='uploads/or/')
        cr_upload = models.FileField(upload_to='uploads/cr/')
        license_upload = models.FileField(upload_to='uploads/license/')
        password = models.CharField(max_length=128, blank=True, null=False)
        qr_code = models.ImageField(upload_to='uploads/qr_codes/', blank=True, null=True)

        def __str__(self):
            return f"{self.username} ({self.student_id})"
        
        def set_password(self, raw_password):
            self.password = make_password(raw_password)
            self.save()

        def check_password(self, raw_password):
            return check_password(raw_password, self.password)
    
    
class Security(models.Model):
    picture = models.ImageField(upload_to='security_pictures/', blank=True, null=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30, unique=True, default='default_username')
    password = models.CharField(max_length=128)
    confirm_password = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    def save(self, *args, **kwargs):
        # Ensure password and confirm_password are hashed before saving
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        if not self.confirm_password.startswith('pbkdf2_sha256$'):
            self.confirm_password = make_password(self.confirm_password)

        super(Security, self).save(*args, **kwargs)
    
class Violation(models.Model):
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    student_id = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=50)
    violations = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.username} - {self.violations} ({self.vehicle_type})"
    
    
class Logs(models.Model):
    LOG_TYPE_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]

    student_id = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    course = models.CharField(max_length=100)
    log_time = models.DateTimeField(default=timezone.now)  # Stores both date and time
    log_type = models.CharField(max_length=10, choices=LOG_TYPE_CHOICES)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.log_type} at {self.log_time.strftime('%Y-%m-%d %H:%M:%S')}"