from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Student, StudentMasterList, Security, Violation,Logs
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
        or_upload=student.or_upload,
        cr_upload=student.cr_upload,
        license_upload=student.license_upload,
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
                request.session['username'] = student.username
                request.session['student_id'] = student.student_id
                
               
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
            student = form.save(commit=False)
       
            student.save()
            messages.success(request, 'Registration successful!')
            return redirect('stud-log')
        else:
            messages.error(request, 'Please correct the errors below.')
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




def custom_logout_view(request):
    logout(request)
    return redirect('head-login')  # Redirect to your desired page


def student_logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('stud-log')

def security_logout_view(request):
    logout(request)
    return redirect('security-login')  # Redirect to your desired page

def student_logout_view(request):
    logout(request) 
    return redirect('stud-log')  # Redirect to your desired page


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
            'or_upload': student.or_upload.url,
            'cr_upload': student.cr_upload.url,
            'license_upload': student.license_upload.url,
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
            'or_upload': student.or_upload.url,
            'cr_upload': student.cr_upload.url,
            'license_upload': student.license_upload.url,
            'qr_code': student.qr_code.url if student.qr_code else '',
        }
        return JsonResponse(data)
    except StudentMasterList.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    
from django.contrib.auth.hashers import check_password

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


def security_dashboard(request):
    return render(request, 'qrapp/security-dashboard.html')


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
                # Check if the QR code data is numeric (student ID)
                if qr_code_data.isnumeric():
                    student = StudentMasterList.objects.get(student_id=qr_code_data)
                    return JsonResponse({
                        'qr_code_data': qr_code_data,
                        'student_name': student.username,
                        'student_id': student.student_id,
                        'first_name': student.first_name,
                        'last_name': student.last_name,
                    })
                else:
                    return JsonResponse({'error': 'Invalid QR code data'})
            
            except StudentMasterList.DoesNotExist:
                return JsonResponse({'error': 'Student not found'})

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
            try:
                if qr_code_data.isnumeric():
                    student = StudentMasterList.objects.get(student_id=qr_code_data)

                    # Get the latest log entry for the student
                    last_log = Logs.objects.filter(student_id=student.student_id).order_by('-log_time').first()

                    # Only create a new log entry if the last state was different
                    if last_log is None or last_log.log_type == 'logout':
                        log_type = 'login'
                    elif last_log.log_type == 'login':
                        log_type = 'logout'

                    # Set interval delay (e.g., 5 seconds)
                    interval_delay = timezone.timedelta(seconds=7)
                    recent_log_exists = (
                        last_log and last_log.log_time >= timezone.now() - interval_delay
                    )

                    if not recent_log_exists:
                        # Create and save the log entry
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
                                'course': student.course,
                                'log_type': log_type,
                            },
                        })
                    else:
                        return JsonResponse({'success': False, 'message': 'Please wait for a few seconds before the next scan.'})

                else:
                    return JsonResponse({'success': False, 'message': 'Invalid QR code data'})
            except StudentMasterList.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Student not found'})

        return JsonResponse({'success': False, 'message': 'QR code not detected'})
    
def student_logs(request):
    logs = Logs.objects.all()  # Retrieve all log entries
    return render(request, 'qrapp/logs.html', {'logs': logs})

    
def submit_violation(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        student_id = request.POST.get('student_id')
        vehicle_type = request.POST.get('vehicle_type')
        violations = request.POST.get('violations')

        # Create a new violation record
        violation = Violation.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            student_id=student_id,
            vehicle_type=vehicle_type,
            violations=violations
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


def violation_list(request):
    violations = Violation.objects.all()
    return render(request, 'qrapp/violations.html', {'violations': violations})

def reject_student(request, student_id):
    # Fetch the student record or return a 404 error if not found
    student = get_object_or_404(StudentMasterList, id=student_id)
    
    # Optionally, you can perform additional actions here, e.g., logging the rejection

    # Delete the student record
    student.delete()
    
    # Add a success message to inform the user
    messages.success(request, 'The registration has been successfully rejected.')
    
    # Redirect to the pending registrations page or another page as needed
    return redirect('pending_registrations')  # Make sure to replace 'pending_registrations' with your actual URL name