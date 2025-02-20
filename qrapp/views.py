from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Student, StudentMasterList, Security, Violation,Logs, Vehicle, EmployeeLogs
from .forms import StudentRegistrationForm  # Create this form separately
from django.contrib import messages
from datetime import datetime
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth import logout
from django.core.files.base import ContentFile
from django.http import JsonResponse
import qrcode
import base64
from django.db import IntegrityError
from io import BytesIO
import cv2
from PIL import Image
import numpy as np
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from .forms import SecurityLoginForm
from django.contrib.auth.hashers import make_password
import threading
from .forms import StudentLoginForm
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.cache import cache
from django.http import StreamingHttpResponse
from .models import Violation
from django.utils import timezone
from django.db.models import Count
from .forms import VehicleForm
from datetime import timedelta
from django.contrib.auth.models import User
from .models import Employee,EmployeeVehicle, EmployeeViolation,EmployeeNotification,EmployeePendingRegistration
from django.utils.timezone import now
from django.db.models import Count,functions

def employee_logs_view(request):
        employee_id = request.session.get('employee_id')
        logs = EmployeeLogs.objects.filter(employee_id=employee_id)
        return render(request, 'qrapp/employee_logs.html', {'logs': logs})

def employee_violations(request):
   
        employee_id = request.session.get('employee_id')  # Retrieve employee ID from session
       # Get the employee instance

        # Retrieve all violations associated with the logged-in employee
        violations = EmployeeViolation.objects.filter(employee_id = employee_id)

        return render(request, 'qrapp/employee-own-violations.html', {
            'violations': violations
        })

        
        
def student_logs_view(request):
 
    # Get the student_id from the session
    student_id = request.session.get('student_id')

    # Query the logs for the logged-in student
    student_logs = Logs.objects.filter(student_id=student_id)

    # Pass the logs to the template
    return render(request, 'qrapp/student-own-logs.html', {'student_logs': student_logs})


def student_violations_view(request):
    # Get the logged-in student's username from the session
    student_id = request.session.get('student_id')
    
    # Filter violations for the logged-in student
    violations = Violation.objects.filter(student_id=student_id)

    context = {
        'violations': violations,
    }
    return render(request, 'qrapp/student-own-violations.html', context)

def employee_notifications(request):
    # Get the logged-in employee's ID from the session
    employee_id = request.session.get('employee_id')

    if employee_id:
        # Fetch notifications for the logged-in employee
        notifications = EmployeeNotification.objects.filter(employee_id=employee_id).order_by('-date_created')
    else:
        notifications = []

    return render(request, 'qrapp/employee-notif.html', {'notifications': notifications})


def submit_employee_violation(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        full_name = request.POST.get('employee_name')  # Adjusted field name to match form
        vehicle_type = request.POST.get('employee_vehicle_type')  # Adjusted field name to match form
        violations = request.POST.get('employee_violation')  # Adjusted field name to match form
        print(f"ID: {employee_id}, Name: {full_name}, Vehicle: {vehicle_type}, Violations: {violations}")
        # Check if the employee already has violation records
        existing_violations = EmployeeViolation.objects.filter(employee_id=employee_id)
        offense_count = existing_violations.count() + 1  # Set offense count based on existing violations

        # Create a new violation record with date_created and offense_count
        EmployeeViolation.objects.create(
            employee_id=employee_id,
            full_name=full_name,
            vehicle_type=vehicle_type,
            violations=violations,
            date_created=timezone.now(),
            offense_count=offense_count,
        )
        
        # Create a notification for the employee
        employee = Employee.objects.get(id=employee_id)
        message = f"You have a new violation: {violations}"
        EmployeeNotification.objects.create(employee=employee, message=message)
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

def security_list(request):
    securities = Security.objects.all()
    return render(request, 'qrapp/security-list.html', {'securities': securities})


def toggle_security_status(request):
    if request.method == 'POST':
        security_id = request.POST.get('security_id')
        is_active = request.POST.get('is_active') == 'true'

        try:
            security = Security.objects.get(id=security_id)
            security.is_active = is_active
            security.save()
            status = "activated" if is_active else "deactivated"
            return JsonResponse({'message': f'Security personnel successfully {status}!'})
        except Security.DoesNotExist:
            return JsonResponse({'message': 'Security personnel not found!'}, status=404)
    return JsonResponse({'message': 'Invalid request method!'}, status=400)


def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'qrapp/employee-list.html', {'employees': employees})

def all_employee_vehicle(request):
    vehicles = EmployeeVehicle.objects.select_related('employee_id').all()
    return render(request, 'qrapp/all_employee_vehicles.html', {'vehicles': vehicles})

def my_vehicle_employee(request):
    # Get the logged-in employee using the session
    employee_id = request.session.get('employee_id')
    
    # Retrieve the employee's vehicles
    vehicles = EmployeeVehicle.objects.filter(employee_id=employee_id)
    
    # Pass the vehicle details to the template
    return render(request, 'qrapp/my_vehicle_employee.html', {'vehicles': vehicles})

def add_employee_vehicle(request):
    if request.method == 'POST':
        plate_number = request.POST['plate_number']
        plate_number_type = request.POST['plate_number_type']
        or_upload = request.FILES['or_upload']
        cr_upload = request.FILES['cr_upload']
        license_upload = request.FILES['license_upload']
        vehicle_type = request.POST['vehicle_type']
        
        
        # Get the employee_id from the session
        employee_id = request.session.get('employee_id')
        
        if not employee_id:
            # Handle the case when employee_id is not found in session
            return redirect('unified-login')  # Redirect to login or appropriate page
        
        # Fetch the employee object using the session's employee_id
        employee = Employee.objects.get(id=employee_id)
        
        # Create the EmployeeVehicle instance
        EmployeeVehicle.objects.create(
            plate_number=plate_number,
            plate_number_type=plate_number_type,
            or_upload=or_upload,
            cr_upload=cr_upload,
            license_upload=license_upload,
            vehicle_type=vehicle_type,
            employee_id=employee  # Use the employee object to associate with the vehicle
        )
        
        return redirect('my-vehicle-employee')  # Redirect to a success page or another view
    
    # If the request is GET, render the form
    return render(request, 'qrapp/add_vehicle_employee.html')


def employee_dashboard(request):
    return render(request, 'qrapp/employee-dashboard.html')

# def employee_form(request):
#     if request.method == 'POST':
#         full_name = request.POST.get('full_name')
#         contact_number = request.POST.get('contact_number')
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         status = request.POST.get('status')

#         # Hash the password
#         hashed_password = make_password(password)

#         # Create the Employee object (initial save)
#         employee = Employee.objects.create(
#             full_name=full_name,
#             contact_number=contact_number,
#             username=username,
#             password=hashed_password,
#             status=status
#         )

#         # Generate QR Code
#         qr = qrcode.QRCode(version=1, box_size=10, border=5)
#         qr.add_data(str(employee.id))  # Just the ID without "Employee ID: "
#         qr.make(fit=True)

#         # Save QR Code to ImageField
#         img = qr.make_image(fill='black', back_color='white')
#         buffer = BytesIO()
#         img.save(buffer, format='PNG')
#         file_name = f'employee_{employee.id}_qr.png'
#         employee.qr_code.save(file_name, ContentFile(buffer.getvalue()))
#         buffer.close()

#         return redirect('unified-login')  # Replace with your desired redirect URL name or view

#     return render(request, 'qrapp/employee-register.html')

def approve_pending_employee(request, pk):
    # Retrieve the pending employee record
    pending_employee = get_object_or_404(EmployeePendingRegistration, pk=pk)

    # Transfer data to the Employee model
    employee = Employee.objects.create(
        full_name=pending_employee.full_name,
        contact_number=pending_employee.contact_number,
        username=pending_employee.username,
        password=pending_employee.password,  # Password is already hashed
        status=pending_employee.status,
    )

    # Generate a QR code for the approved employee
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(str(employee.id))
    qr.make(fit=True)

    # Save the QR code as an image
    img = qr.make_image(fill="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    file_name = f'employee_{employee.id}_qr.png'
    employee.qr_code.save(file_name, ContentFile(buffer.getvalue()))
    buffer.close()

    # Delete the pending record after approval
    pending_employee.delete()

    # Return success response or redirect
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # For AJAX requests
        return JsonResponse({'success': True, 'message': 'Employee approved successfully!'})
    return redirect('pending-registrations')  # Replace with your desired URL

def employee_form(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        contact_number = request.POST.get('contact_number')
        username = request.POST.get('username')
        password = request.POST.get('password')
        status = request.POST.get('status')

        # Hash the password
        hashed_password = make_password(password)

        # Save to EmployeePendingRegistration model
        pending_employee = EmployeePendingRegistration.objects.create(
            full_name=full_name,
            contact_number=contact_number,
            username=username,
            password=hashed_password,
            status=status
        )

        return redirect('unified-login')  # Replace with your desired redirect URL name or view

    return render(request, 'qrapp/employee-register.html')

def unified_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check for Student
        try:
            student = StudentMasterList.objects.get(username=username)
            if student.check_password(password):
                # Log the student in
                request.session['user_type'] = 'student'
                request.session['student_id'] = student.student_id
                request.session['first_name'] = student.first_name
                request.session['last_name'] = student.last_name
                return redirect('stud-dashboard')
        except StudentMasterList.DoesNotExist:
            pass

        # Check for Security
        try:
            security_officer = Security.objects.get(username=username)
            if check_password(password, security_officer.password):
                # Log the security officer in
                request.session['user_type'] = 'security'
                request.session['username'] = username
                request.session['security_picture'] = security_officer.picture.url if security_officer.picture else None
                return redirect('security-dashboard')
        except Security.DoesNotExist:
            pass
         # Check for Employee
        try:
            employee = Employee.objects.get(username=username)
            if check_password(password, employee.password):  # Use check_password for comparison
                request.session['user_type'] = 'employee'
                request.session['employee_id'] = employee.id
                request.session['full_name'] = employee.full_name
                return redirect('employee-dashboard')
        except Employee.DoesNotExist:
            pass
        
        
        # Check for Built-in User (Head)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Assume the built-in user is the head
            request.session['user_type'] = 'head'
            messages.success(request, 'Login successful!')
            return redirect('head-dashboard')

        # If none of the conditions match, return an error message
        messages.error(request, 'Invalid username or password.')

    return render(request, 'qrapp/u_login.html')


def all_vehicles(request):
    student_vehicles = Vehicle.objects.all()
    employee_vehicles = EmployeeVehicle.objects.all()

    context = {
        'student_vehicles': student_vehicles,
        'employee_vehicles': employee_vehicles,
    }
    return render(request, 'qrapp/all_vehicles.html', context)

def approve_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # Generate activation link
    token = get_random_string(length=32)  # Create a unique token
    cache.set(token, student.id, timeout=3600)  # Store token with student ID for 1 hour

    activation_link = request.build_absolute_uri(reverse('activate_student', args=[token]))

    # Send activation email directly here
    subject = 'Activate Your Account'
    message = f'Please activate your account by clicking the link: {activation_link}'
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(
        subject,
        message,
        from_email,
        [student.email],
        fail_silently=False,
    )
    
    messages.success(request, "Email sent!.")
    return redirect('pending-registration')


def activate_student(request, token):
    student_id = cache.get(token)

    if not student_id:
        messages.error(request, "Invalid or expired activation link.")
        return redirect('some_error_page')  # Redirect to an error page

    student = get_object_or_404(Student, id=student_id)

    # Move student data to StudentMasterList
    student_master = StudentMasterList(
        student_id=student.student_id,
        username=student.username,
        first_name=student.first_name,  # Add first_name field
        last_name=student.last_name,    # Add last_name field
        email=student.email,
        course=student.course,
        year=student.year,
        major=student.major,
        # or_upload=student.or_upload,
        # cr_upload=student.cr_upload,
        # license_upload=student.license_upload,
        password=student.password,
    )
    student_master.set_password(student.password)  # Hash the password
    student_master.save()

    # Generate QR code with only the student_id
    qr_data = f"{student_master.student_id}"
    qr_image = qrcode.make(qr_data)
    
    # Save QR code to the model
    buffer = BytesIO()
    qr_image.save(buffer, format='PNG')
    qr_code_file = ContentFile(buffer.getvalue(), name=f"{student_master.student_id}_qr.png")
    student_master.qr_code.save(f"{student_master.student_id}_qr.png", qr_code_file)

    # Optionally delete the student record after activation
    student.delete()

    messages.success(request, "Your account has been activated successfully.")
    return redirect('stud-log')  # Redirect to a success page

def home(request):
   
    if request.session.get('student_id'):
        return redirect('stud-dashboard')
    if request.user.is_authenticated:
        return redirect('head-dashboard')
    if request.session.get('user_type') == 'security':
            return redirect('security-dashboard')
    
    return render(request, 'qrapp/index.html')


def student_own_profile(request):
    student_id = request.session.get('student_id')
    if not student_id:
        # Redirect or handle the case where the student_id is not in session
        return redirect('unified-login')  # Adjust the URL name as per your project

    # Retrieve the student's data
    student = get_object_or_404(StudentMasterList, student_id=student_id)
    
    vehicles = Vehicle.objects.filter(student_id=student)
    
    logs = Logs.objects.filter(student_id=student_id).order_by('-log_time')
    
    violations = Violation.objects.filter(student_id=student_id)

    return render(request, 'qrapp/student-own-profile.html', {'student': student, 'vehicles': vehicles,  'logs': logs , 'violations': violations})



def update_student_profile(request):
    if request.method == 'POST':
        student_id = request.session.get('student_id')
        student = get_object_or_404(StudentMasterList, student_id=student_id)

        # Update profile fields
        student.first_name = request.POST.get('first_name', student.first_name)
        student.last_name = request.POST.get('last_name', student.last_name)
        student.email = request.POST.get('email', student.email)
        student.course = request.POST.get('course', student.course)
        student.year = request.POST.get('year', student.year)
        student.major = request.POST.get('major', student.major)

        # Update password if provided
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password and confirm_password:
            if password == confirm_password:
                student.password = make_password(password)
            else:
                messages.error(request, 'Passwords do not match.')
                return redirect('student-own-profile')  # Adjust the URL name as needed

        student.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('student-own-profile')

    return redirect('student-own-profile')

def login_stud(request):
    
    if request.user.is_authenticated:
        return redirect('head-dashboard')

    form = StudentLoginForm(request.POST or None)  # Instantiate the form

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        
        # Try to get the student by username
        try:
            student = StudentMasterList.objects.get(username=username)
            if student.check_password(password):  # Use the method here
                # Log the student in
                request.session['user_type'] = 'student'
                request.session['student_id'] = student.student_id
                request.session['first_name'] = student.first_name  # Store first name
                request.session['last_name'] = student.last_name 
                
               
                return redirect('stud-dashboard')
            else:
                messages.error(request, "Invalid password.")
        except StudentMasterList.DoesNotExist:
            messages.error(request, "No student found with that username.")
    
    return render(request, 'qrapp/login.html', {'form': form})



def student_dashboard(request):
    return render(request, 'qrapp/stud-dashboard.html')

def register_stud(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Check if email already exists in the database
                if StudentMasterList.objects.filter(email=form.cleaned_data['email']).exists():
                    messages.error(request, "This email is already registered. Please use a different one.")
                    return render(request, 'qrapp/register.html', {'form': form})

                # Create student if the email is unique
                student_master = StudentMasterList(
                    student_id=form.cleaned_data['student_id'],
                    username=form.cleaned_data['username'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    course=form.cleaned_data['course'],
                    year=form.cleaned_data['year'],
                    major=form.cleaned_data['major'],
                )
                # Hash and save the password
                student_master.set_password(form.cleaned_data['password'])
                
                # Generate QR code
                qr_data = f"{student_master.student_id}"
                qr_image = qrcode.make(qr_data)
                buffer = BytesIO()
                qr_image.save(buffer, format='PNG')
                qr_code_file = ContentFile(buffer.getvalue(), name=f"{student_master.student_id}_qr.png")
                student_master.qr_code.save(f"{student_master.student_id}_qr.png", qr_code_file)

                # Save student record
                student_master.save()

                messages.success(request, "Registration successful. You can now log in.")
                return redirect('unified-login')  # Redirect to login page after registration
            except IntegrityError:
                messages.error(request, "There was an error during registration. Please try again.")
        else:
            messages.error(request, "There was an error with your registration. Please check the form.")
    else:
        form = StudentRegistrationForm()

    return render(request, 'qrapp/register.html', {'form': form})

def dashboard(request):
    return render(request, 'qrapp/dashboard.html')

def head_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('head-dashboard')  # Redirect to your desired page after login
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'qrapp/head-login.html', {'form': form})

def head_dashboard(request):
    return render(request, 'qrapp/head-dashboard.html')

def student_violations_analytics(request):
    violations_by_month = (
        Violation.objects.annotate(month=functions.ExtractMonth('date_created'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    data = {month: 0 for month in range(1, 13)}  # Initialize months with 0
    for entry in violations_by_month:
        data[entry['month']] = entry['count']

    return JsonResponse({'months': list(data.keys()), 'violations': list(data.values())})


def employee_violations_analytics(request):
    violations_by_month = (
        EmployeeViolation.objects.annotate(month=functions.ExtractMonth('date_created'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    data = {month: 0 for month in range(1, 13)}  # Initialize months with 0
    for entry in violations_by_month:
        data[entry['month']] = entry['count']

    return JsonResponse({'months': list(data.keys()), 'violations': list(data.values())})


def analytics_data(request):
    # Calculate new users in the last 5 months
    today = datetime.now()
    months = [(today - timedelta(days=30 * i)).strftime("%b") for i in range(4, -1, -1)]
      # Calculate total students and employees
    total_students = StudentMasterList.objects.count()
    total_employees = Employee.objects.count()

    student_counts = [
        StudentMasterList.objects.filter(
            created_at__year=(today - timedelta(days=30 * i)).year,
            created_at__month=(today - timedelta(days=30 * i)).month
        ).count()
        for i in range(4, -1, -1)
    ]
    
    employee_counts = [
        Employee.objects.filter(
            created_at__year=(today - timedelta(days=30 * i)).year,
            created_at__month=(today - timedelta(days=30 * i)).month
        ).count()
        for i in range(4, -1, -1)
    ]
    
    return JsonResponse({
        'months': months,
        'students': student_counts,
        'employees': employee_counts,
        'total_students': total_students,
        'total_employees': total_employees,
    })

def logs_analytics_data(request):
    # Aggregate logs data
    student_logs = Logs.objects.values('log_type').annotate(count=Count('log_type'))
    employee_logs = EmployeeLogs.objects.values('log_type').annotate(count=Count('log_type'))
    
    student_data = {log['log_type']: log['count'] for log in student_logs}
    employee_data = {log['log_type']: log['count'] for log in employee_logs}

    data = {
        'students': student_data,
        'employees': employee_data,
    }
    return JsonResponse(data)

def student_list(request):
    # Fetch all students from the StudentMasterList model
    master_list_students = StudentMasterList.objects.all()

    # Render the master list template with the fetched students
    return render(request, 'qrapp/student-list.html', {
        'master_list_students': master_list_students
    })

def pending_registration(request):
    # Fetch all student registrations (update the filter as needed)
    registrations = Student.objects.all()  # Ensure you're filtering for pending registrations if necessary

    # Pass registrations as a dictionary
    context = {'registrations': registrations}
    
    return render(request, 'qrapp/pending-registration.html', context)

def employee_pending(request):
    pending_employees = EmployeePendingRegistration.objects.all()
    return render(request, 'qrapp/employee-pending-registrations.html', {'pending_employees': pending_employees})

def custom_logout_view(request):
    logout(request)
    return redirect('unified-login')  # Redirect to your desired page


def student_logout_view(request):
    logout(request)
   
    return redirect('unified-login')

def security_logout_view(request):
    logout(request)
    return redirect('unified-login')  # Redirect to your desired page

# def student_logout_view(request):
#     logout(request) 
#     return redirect('stud-log')  # Redirect to your desired page


def student_details_pending(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
        data = {
            'username': student.username,
            'email': student.email,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'course': student.course,
            'year': student.year,
            'major': student.major,
            # 'or_upload': student.or_upload.url,
            # 'cr_upload': student.cr_upload.url,
            # 'license_upload': student.license_upload.url,
        }
        return JsonResponse(data)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    

def update_student(request):
    if request.method == 'POST':
        student_id = request.POST.get('id')  # Match the 'id' passed in the form
        student = get_object_or_404(StudentMasterList, id=student_id)
        
        # Update student fields
        student.username = request.POST.get('username')
        student.email = request.POST.get('email')
        student.course = request.POST.get('course')
        student.year = request.POST.get('year')
        student.major = request.POST.get('major')
        
        # Save the updated student details
        student.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

    
def generate_qr_code(request):
    data = request.GET.get('data', None)
    qr_code_url = None

    if data:
        # Generate the QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        # Save the image to a BytesIO object
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Encode the image to Base64
        qr_code_url = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render(request, 'qrapp/generate-qr.html', {'qr_code_url': qr_code_url, 'data': data})


def student_details(request):
    student_id = request.GET.get('student_id')
    try:
        student = StudentMasterList.objects.get(id=student_id)
        data = {
            'student_id': student.student_id,
            'username': student.username,
            'email': student.email,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'course': student.course,
            'year': student.year,
            'major': student.major,
            # 'or_upload': student.or_upload.url,
            # 'cr_upload': student.cr_upload.url,
            # 'license_upload': student.license_upload.url,
            'qr_code': student.qr_code.url if student.qr_code else '',
        }
        return JsonResponse(data)
    except StudentMasterList.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    
def security_login(request):
    if request.method == 'POST':
        form = SecurityLoginForm(request.POST)
        if form.is_valid():
            # Get the form data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Check if the user exists in the Security model
            try:
                security_officer = Security.objects.get(username=username)
                
                # Check if the password matches using check_password
                if check_password(password, security_officer.password):
                    # Save the user type in session and redirect to dashboard
                    request.session['user_type'] = 'security'
                    request.session['username'] = username
                    request.session['security_picture'] = security_officer.picture.url if security_officer.picture else None
                    
                    return redirect('security-dashboard')
                else:
                    # If password doesn't match
                    messages.error(request, 'Invalid password.')
            except Security.DoesNotExist:
                # If the username doesn't exist in the database
                messages.error(request, 'Username not found.')
    else:
        form = SecurityLoginForm()

    return render(request, 'qrapp/security-login.html', {'form': form}) 


def security_own_profile(request):
    # Check if the logged-in user is a security officer
    if request.session.get('user_type') == 'security':
        username = request.session.get('username')
        try:
            officer = Security.objects.get(username=username)
        except Security.DoesNotExist:
            officer = None
        
        return render(request, 'qrapp/security-own-profile.html', {'officer': officer})
    else:
        # Redirect to login if not authenticated as a security officer
        return redirect('unified_login')

def update_security_profile(request):
    if request.session.get('user_type') == 'security':
        username = request.session.get('username')
        try:
            officer = Security.objects.get(username=username)
        except Security.DoesNotExist:
            messages.error(request, "Security officer not found.")
            return redirect('security-own-profile')

        if request.method == 'POST':
            # Update text fields
            officer.first_name = request.POST.get('first_name')
            officer.last_name = request.POST.get('last_name')
            officer.username = request.POST.get('username')

            # Update profile picture
            if 'picture' in request.FILES:
                officer.picture = request.FILES['picture']

            # Validate and update password
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password and confirm_password:
                if password == confirm_password:
                    officer.password = make_password(password)
                else:
                    messages.error(request, "Passwords do not match.")
                    return render(request, 'qrapp/security-own-profile.html', {'officer': officer})

            officer.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('security-own-profile')

        return render(request, 'qrapp/security-profile.html', {'officer': officer})
    else:
        return redirect('unified_login')
    

def reject_student(request, student_id):
    # Fetch the student registration by ID
    student = get_object_or_404(Student, id=student_id)
    
    # Delete the student registration (rejecting the student)
    student.delete()

    # After rejection, redirect back to the list of pending registrations
    return redirect('pending-registration')  # Replace 'pending-registration' with your URL name



def security_dashboard(request):
    violations = Violation.objects.all()  # Get violations from Violation model
    employee_violations = EmployeeViolation.objects.all()  # Get violations from EmployeeViolation model

    # Merge both sets of violations
    all_violations = list(violations) + list(employee_violations)

    return render(request, 'qrapp/security-dashboard.html', {'violations': all_violations})


def qr_code_scanner_view(request):
    violations = Violation.objects.all()  # Fetch all violations from the database
    return render(request, 'qrapp/camera_qr_scanner.html', {'violations': violations})
    
@csrf_exempt
def scan_qr_code(request):
    if request.method == 'POST':
        image_data = request.FILES.get('frame')
        
        # Convert image to a format suitable for OpenCV
        file_bytes = np.frombuffer(image_data.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Preprocessing for better QR detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(blur, -1, sharpen_kernel)

        # Resize dynamically to improve detection from a distance
        resized_img = cv2.resize(sharpened, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)

        # QR code detection
        qr_detector = cv2.QRCodeDetector()
        qr_code_data, points, _ = qr_detector.detectAndDecode(resized_img)

        if qr_code_data:
            try:
                # Check if the QR code data is numeric (student ID or employee ID)
                if qr_code_data:
                    # Try fetching student first
                    print(f"QR Code Data: {qr_code_data}") 
                    try:
                        student = StudentMasterList.objects.get(student_id=qr_code_data)
                        offense_count = Violation.objects.filter(student_id=qr_code_data).count()
                        print(student.username)
                        vehicles = Vehicle.objects.filter(student_id=student)
                        for vehicle in vehicles:
                            print(vehicle)

                        response_data = {
                            'qr_code_data': qr_code_data,
                            'student_name': student.username,
                            'student_id': student.student_id,
                            'first_name': student.first_name,
                            'last_name': student.last_name,
                            'offense_count': offense_count
                        }

                        vehicle_options = []
                        for vehicle in vehicles:
                            vehicle_options.append({
                                'vehicle_type': vehicle.vehicle_type,
                                'plate_number': vehicle.plate_number
                            })

                        response_data['vehicles'] = vehicle_options
                        return JsonResponse(response_data)

                    except StudentMasterList.DoesNotExist:
                        pass  # If no student found, proceed to employee check

                    # Now check for employee
                    try:
                        employee = Employee.objects.get(id=int(qr_code_data))  
                        print(f"Employee Data: {employee.full_name}, ID: {employee.id}, Contact: {employee.contact_number}, Status: {employee.status}")
                        vehicles = EmployeeVehicle.objects.filter(employee_id=employee.id)  # Assuming `employee_id` is the foreign key
                        for vehicle in vehicles:
                            print(vehicle)
                        response_data = {
                            'qr_code_data': qr_code_data,
                            'employee_name': employee.full_name,
                            'employee_id': employee.id, 
                            'contact_number': employee.contact_number,
                            'status': employee.status
                        }
                        
                        vehicle_options = []
                        for vehicle in vehicles:
                                vehicle_options.append({
                                    'vehicle_type': vehicle.vehicle_type,
                                    'plate_number': vehicle.plate_number
                                })

                        response_data['vehicles'] = vehicle_options

                        return JsonResponse(response_data)

                    except Employee.DoesNotExist:
                        return JsonResponse({'error': 'Employee not found'})

                else:
                    return JsonResponse({'error': 'Invalid QR code data'})

            except Exception as e:
                return JsonResponse({'error': str(e)})

        return JsonResponse({'error': 'QR code not detected'})

def attendance_scanner(request):
    return render(request, 'qrapp/attendance-scanner.html')

@csrf_exempt
def scan_student_qr_code(request):
    if request.method == 'POST':
        image_data = request.FILES.get('frame')
        if not image_data:
            return JsonResponse({'success': False, 'message': 'No image data found'})

        # Convert image data for OpenCV processing
        file_bytes = np.frombuffer(image_data.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Process image for QR code detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(blur, -1, sharpen_kernel)
        resized_img = cv2.resize(sharpened, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)

        # Detect and decode QR code
        qr_detector = cv2.QRCodeDetector()
        qr_code_data, points, _ = qr_detector.detectAndDecode(resized_img)

        if qr_code_data:
            print(f"Detected QR Code Data: {qr_code_data}")  # Print the QR code data
            try:
                # Check if QR code belongs to a student
                student = StudentMasterList.objects.get(student_id=qr_code_data)

                # Get the latest log entry for the student
                last_log = Logs.objects.filter(student_id=student.student_id).order_by('-log_time').first()

                # Determine log type for the student
                if last_log is None or last_log.log_type == 'logout':
                    log_type = 'login'
                elif last_log.log_type == 'login':
                    log_type = 'logout'

                # Set interval delay (e.g., 7 seconds)
                interval_delay = timezone.timedelta(seconds=7)
                recent_log_exists = (
                    last_log and last_log.log_time >= timezone.now() - interval_delay
                )

                if not recent_log_exists:
                    # Create and save the student log entry
                    log_entry = Logs(
                        student_id=student.student_id,
                        first_name=student.first_name,
                        last_name=student.last_name,
                        course=student.course,
                        log_time=timezone.now(),
                        log_type=log_type
                    )
                    log_entry.save()

                    return JsonResponse({
                        'success': True,
                        'student': {
                            'student_id': student.student_id,
                            'username': student.username,
                            'first_name': student.first_name,
                            'last_name': student.last_name,
                            'course': student.course,
                            'log_type': log_type,
                            'log_time': log_entry.log_time.strftime('%Y-%m-%d %H:%M:%S'),
                        },
                    })
                else:
                    return JsonResponse({'success': False, 'message': 'Please wait for a few seconds before the next scan.'})

            except StudentMasterList.DoesNotExist:
                try:
                    # Check if QR code belongs to an employee
                    employee = Employee.objects.get(id=qr_code_data)
                    
                    print(f"Employee QR Data Detected: {qr_code_data}")
                    print(f"Employee Full Name: {employee.full_name}")
                    print(f"Employee Status: {employee.status}")
                    # Get the latest log entry for the employee
                    last_log = EmployeeLogs.objects.filter(employee=employee).order_by('-log_time').first()

                    # Determine log type for the employee
                    if last_log is None or last_log.log_type == 'logout':
                        log_type = 'login'
                    elif last_log.log_type == 'login':
                        log_type = 'logout'

                    # Set interval delay (e.g., 7 seconds)
                    interval_delay = timezone.timedelta(seconds=7)
                    recent_log_exists = (
                        last_log and last_log.log_time >= timezone.now() - interval_delay
                    )

                    if not recent_log_exists:
                        # Create and save the employee log entry
                        log_entry = EmployeeLogs(
                            employee=employee,
                            log_time=timezone.now(),
                            log_type=log_type
                        )
                        log_entry.save()
                        return JsonResponse({
                            'success': True,
                            'employee': {
                                'id': employee.id,
                                'full_name': employee.full_name,
                                'username': employee.username,
                                'contact_number': employee.contact_number,
                                'status': employee.status,
                                'log_type': log_type,
                                'log_time': log_entry.log_time.strftime('%Y-%m-%d %H:%M:%S'),
                            },
                        })
                    else:
                        return JsonResponse({'success': False, 'message': 'Please wait for a few seconds before the next scan.'})

                except Employee.DoesNotExist:
                    return JsonResponse({
                        "success": False,
                        "qr_detected": True,
                        "message": "QR code does not match any student or employee"
                    })  # QR detected but no match

        return JsonResponse({'success': False, 'message': 'QR code not detected'})

    
def mobile_attendance_scanner(request):
    return render(request, 'qrapp/mobile-attendance-scanner.html')
    
def student_logs(request):
    logs = Logs.objects.all()

    # Handle timeframe filter
    timeframe = request.GET.get('timeframe', '')
    if timeframe:
        if timeframe == 'today':
            today = timezone.now().date()
            logs = logs.filter(log_time__date=today)
        elif timeframe == 'last_7_days':
            last_7_days = timezone.now() - timedelta(days=7)
            logs = logs.filter(log_time__gte=last_7_days)
        elif timeframe == 'last_30_days':
            last_30_days = timezone.now() - timedelta(days=30)
            logs = logs.filter(log_time__gte=last_30_days)

    # Handle start and end date filters
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    if start_date:
        logs = logs.filter(log_time__gte=start_date)
    if end_date:
        logs = logs.filter(log_time__lte=end_date)

    return render(request, 'qrapp/logs.html', {'logs': logs, 'start_date': start_date, 'end_date': end_date})

    
def submit_violation(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        student_id = request.POST.get('student_id')
        vehicle_type = request.POST.get('vehicle_type')
        violations = request.POST.get('violations')
        
        # Check if the student already has violation records
        existing_violations = Violation.objects.filter(student_id=student_id)
        offense_count = existing_violations.count() + 1  # Set offense count based on existing violations

        # Create a new violation record with date_created and offense_count
        violation = Violation.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            student_id=student_id,
            vehicle_type=vehicle_type,
            violations=violations,
            date_created=timezone.now(),
            offense_count=offense_count
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})


def violation_list(request):
    violations = Violation.objects.all()
    employee_violations = EmployeeViolation.objects.all()
    return render(request, 'qrapp/violations.html', {'violations': violations,'employee_violations': employee_violations})



def my_vehicle(request):
    if 'student_id' not in request.session:
        messages.error(request, "You must be logged in to view your vehicles.")
        return redirect('login_stud')
    
    student_id = request.session['student_id']
    vehicles = Vehicle.objects.filter(student_id__student_id=student_id)  # Filter by logged-in student's ID

    return render(request, 'qrapp/my-vehicle.html', {'vehicles': vehicles})

def add_vehicle(request):
    form = VehicleForm(request.POST, request.FILES)

    if request.method == "POST":
        if form.is_valid():
            vehicle = form.save(commit=False)

            try:
                # Get student by student_id from session
                student = StudentMasterList.objects.get(student_id=request.session['student_id'])
                vehicle.student_id = student  # Assign student instance
                
                vehicle.save()
                messages.success(request, "Vehicle added successfully.")
                return redirect('my-vehicle')
            except StudentMasterList.DoesNotExist:
                messages.error(request, "Student not found. Please log in again.")
        else:
            messages.error(request, "Please correct the errors below.")
    
    return render(request, 'qrapp/add_vehicle.html', {'form': form})



def register_security(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        picture = request.FILES.get('picture')

        # Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'qrapp/register_security.html')

        if Security.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'qrapp/register_security.html')

        # Save Security officer (Removed confirm_password from the model)
        security = Security(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=make_password(password),  # Hash password before saving
            picture=picture
        )
        security.save()

        messages.success(request, "Security officer registered successfully.")
        return redirect('register_security')  # Update this redirect as needed

    return render(request, 'qrapp/register_security.html')

def employee_own_profile(request):
    # Check if the logged-in user is an employee
    if request.session.get('user_type') == 'employee':
        try:
            employee_id = request.session.get('employee_id')
            employee = Employee.objects.get(id=employee_id)
            return render(request, 'qrapp/employee-own-profile.html', {'employee': employee})
        except Employee.DoesNotExist:
            return redirect('unified-login')  # Redirect to login if employee not found
    else:
        return redirect('unified-login')  # Redirect to login if user is not an employee
    
    

def update_employee_profile(request):
    if request.method == 'POST':
        employee_id = request.session.get('employee_id')
        try:
            employee = Employee.objects.get(id=employee_id)
            # Update specific fields
            employee.contact_number = request.POST.get('contact_number')
            employee.username = request.POST.get('username')

            # Handle password update
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password:
                if new_password == confirm_password:
                    employee.password = make_password(new_password)  # Hash password
                else:
                    # Passwords don't match, handle accordingly
                    messages.error(request, "Passwords do not match.")
                    return redirect('employee-own-profile')

            employee.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('employee-own-profile')
        except Employee.DoesNotExist:
            return redirect('unified-login')  # Redirect if employee not found
    return redirect('employee-own-profile')