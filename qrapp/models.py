from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

from django.utils import timezone

class User(AbstractUser):
    # Additional fields for your custom user model
    user_type = models.CharField(max_length=20, choices=[('security', 'Security'), ('student', 'Student'), ('head', 'Head of Security'),('employee', 'Employee') ])

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
    COURSE_CHOICES = [
        ('CAS', 'CAS'),
        ('COTE', 'COTE'),
        ('COMED', 'COMED'),
        ('CTE', 'CTE'),
        ('CGS', 'CGS'),
    ]

    student_id = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    course = models.CharField(max_length=100, choices=COURSE_CHOICES)
    year = models.CharField(max_length=10)
    major = models.CharField(max_length=100)
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
        # or_upload = models.FileField(upload_to='uploads/or/')
        # cr_upload = models.FileField(upload_to='uploads/cr/')
        # license_upload = models.FileField(upload_to='uploads/license/')
        password = models.CharField(max_length=128, blank=True, null=False)
        qr_code = models.ImageField(upload_to='uploads/qr_codes/', blank=True, null=True)
        created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


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
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super(Security, self).save(*args, **kwargs)

    
class Violation(models.Model):
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    student_id = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=50)
    violations = models.CharField(max_length=255)
    date_created = models.DateTimeField(default=timezone.now)  # Field for the date of the violation
    offense_count = models.PositiveIntegerField(blank=True, null=True)  # Field for number of offenses

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

    
    
class Vehicle(models.Model):
    PLATE_TYPE_CHOICES = [
        ('temporary', 'Temporary Plate'),
        ('permanent', 'Permanent Plate'),
        ('improvised', 'Improvised Plate'),
    ]
    plate_number = models.CharField(max_length=20, unique=True)
    plate_type = models.CharField(max_length=15, choices=PLATE_TYPE_CHOICES, null=True, blank=True)  # Add this field
    or_upload = models.FileField(upload_to='uploads/or/')
    cr_upload = models.FileField(upload_to='uploads/cr/')
    license_upload = models.FileField(upload_to='uploads/license/')
    vehicle_type = models.CharField(max_length=50, choices=[('Car', 'Car'), ('Motorcycle', 'Motorcycle')])
    student_id = models.ForeignKey('StudentMasterList', on_delete=models.CASCADE, related_name='vehicles')
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return f"{self.plate_number} ({self.vehicle_type}) - {self.student_id.username}"
    

class EmployeeVehicle(models.Model):
    PLATE_TYPE_CHOICES = [
        ('temporary', 'Temporary Plate'),
        ('permanent', 'Permanent Plate'),
        ('improvised', 'Improvised Plate'),
    ]
    plate_number = models.CharField(max_length=20, unique=True)
    plate_number_type = models.CharField(max_length=15, choices=PLATE_TYPE_CHOICES, null=True, blank=True)
    or_upload = models.FileField(upload_to='uploads/or/')
    cr_upload = models.FileField(upload_to='uploads/cr/')  
    license_upload = models.FileField(upload_to='uploads/license/')
    vehicle_type = models.CharField(max_length=50, choices=[('Car', 'Car'), ('Motorcycle', 'Motorcycle')])
    employee_id = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='vehicles')
    id = models.AutoField(primary_key=True)
    

    def __str__(self):
        return f"{self.plate_number} ({self.vehicle_type}) - {self.employee_id.username}"

class Employee(models.Model):
    STATUS_CHOICES = [
        ('regular', 'Regular'),
        ('contract', 'Contract of Service'),
    ]

    id = models.AutoField(primary_key=True)  # Auto-increment primary key
    full_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    username = models.CharField(max_length=150, unique=True)  # Unique username
    password = models.CharField(max_length=128)  # Password field
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)  # Nullable QR code field
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


    def __str__(self):
        return self.full_name
    
    
class EmployeeLogs(models.Model):
    LOG_TYPE_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]

    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='logs')
    log_time = models.DateTimeField(default=timezone.now)  # Stores both date and time
    log_type = models.CharField(max_length=10, choices=LOG_TYPE_CHOICES)

    def __str__(self):
        return f"{self.employee.full_name} - {self.log_type} at {self.log_time.strftime('%Y-%m-%d %H:%M:%S')}"


class EmployeePendingRegistration(models.Model):
    STATUS_CHOICES = [
        ('regular', 'Regular'),
        ('contract', 'Contract of Service'),
    ]

    id = models.AutoField(primary_key=True)  # Auto-increment primary key
    full_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    username = models.CharField(max_length=150, unique=True)  # Unique username
    password = models.CharField(max_length=128)  # Password field
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    
   
    def __str__(self):
        return f"{self.full_name} (Pending Registration)"    

class EmployeeViolation(models.Model):
    employee_id = models.CharField(max_length=20)
    full_name = models.CharField(max_length=255, blank=True, null=True)  # Full name of the employee
    vehicle_type = models.CharField(max_length=50)
    violations = models.CharField(max_length=255)
    date_created = models.DateTimeField(default=timezone.now)  # Date of violation
    offense_count = models.PositiveIntegerField(blank=True, null=True)  # Number of offenses

    def __str__(self):
        return f"{self.full_name} - {self.violations} ({self.vehicle_type})"


class EmployeeNotification(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)  # Mark if the notification is read
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Notification for {self.employee}: {self.message}"