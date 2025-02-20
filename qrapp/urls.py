from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from .views import custom_logout_view
from .views import security_logout_view
from .views import student_logout_view
from .views import submit_violation
from .views import submit_employee_violation
from .views import reject_student
from . import views 
from .views import approve_student, activate_student, unified_login, logs_analytics_data,employee_violations_analytics
from .views import student_violations_analytics,toggle_security_status



urlpatterns = [
   
    path('',views.home, name=""),
    path('stud-log', views.login_stud, name='stud-log'),
    path('stud-dashboard', views.student_dashboard, name='stud-dashboard'),
    path('stud-reg', views.register_stud, name='stud-reg'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('head-login', views.head_login, name='head-login'),
    path('head-dashboard', views.head_dashboard, name='head-dashboard'),
    path('pending-registration', views.pending_registration, name='pending-registration'),
    path('logout/', custom_logout_view, name='logout'),
    path('stud-logout/', student_logout_view, name='stud-logout'),
    path('security-logout/', security_logout_view, name='security-logout'),
    path('student-details/<int:student_id>/', views.student_details_pending, name='student_details_pending'),
    path('student-list', views.student_list, name='student-list'),
    path('attendance-scanner', views.attendance_scanner, name='attendance-scanner'),
    path('generate-qr-code/', views.generate_qr_code, name='generate_qr_code'),
    path('student-details/', views.student_details, name='student_details'),  # AJAX endpoint
    path('security-login', views.security_login, name='security-login'),  # AJAX endpoint
    path('security-dashboard', views.security_dashboard, name='security-dashboard'),  # AJAX endpoint
    path('qr_code_scanner/', views.qr_code_scanner_view, name='qr_code_scanner'),
    path('scan_qr_code/', views.scan_qr_code, name='scan_qr_code'),
    path('submit_violation/', submit_violation, name='submit_violation'),   
    path('violation_list/', views.violation_list, name='violation_list'),
    path('student/update/', views.update_student, name='update_student'),
    path('approve/<int:student_id>/', approve_student, name='approve_student'),
    path('activate/<str:token>/', activate_student, name='activate_student'),
    path('scan-student-qr/', views.scan_student_qr_code, name='scan_student_qr_code'),
    path('logs/', views.student_logs, name='logs'),
    path('my-vehicle/', views.my_vehicle, name='my-vehicle'),
    path('add-vehicle/', views.add_vehicle, name='add-vehicle'),
    path('all-vehicles/', views.all_vehicles, name='all-vehicles'),
    path('unified-login/', unified_login, name='unified-login'),
    path('employee-reg/', views.employee_form, name='employee-reg'),
    path('employee-dashboard/', views.employee_dashboard, name='employee-dashboard'),
    path('add-vehicle-employee/', views.add_employee_vehicle, name='add-vehicle-employee'),
    path('my-vehicle-employee/', views.my_vehicle_employee, name='my-vehicle-employee'),
    path('all-employee-vehicle/', views.all_employee_vehicle, name='all-employee-vehicle'),
    path('employee-list/', views.employee_list, name='employee-list'),
    path('submit_employee_violation/', submit_employee_violation, name='submit_employee_violation'),
    path('employee-notifications/', views.employee_notifications, name='employee-notifications'),
    path('employee-pending/', views.employee_pending, name='employee-pending'),
    path('approve-employee/<int:pk>/', views.approve_pending_employee, name='approve-employee'), 
    path('mobile-attendance-scan/', views.mobile_attendance_scanner, name='mobile-attendance-scan'), 
    path('violations/', views.student_violations_view, name='student-violations'),
    path('student-logs/', views.student_logs_view, name='student_logs_view'),
    path('employee-violations/', views.employee_violations, name='employee-violations'),
    path('employee-logs/', views.employee_logs_view, name='employee-logs'),
    path('logs-analytics-data/', logs_analytics_data, name='logs_analytics_data'),
    path('analytics-data/', views.analytics_data, name='analytics-data'),
    path('student-violations-data/', student_violations_analytics, name='student_violations_data'),
    path('employee-violations-analytics/', employee_violations_analytics, name='employee_violations_analytics'),
    path('student-own-profile/', views.student_own_profile, name="student-own-profile"),
     path('update-profile/', views.update_student_profile, name='update_student_profile'),
     path('register-security/', views.register_security, name='register_security'),
     path('security-own-profile/', views.security_own_profile, name='security-own-profile'),
     path('update-security-profile/', views.update_security_profile, name='update_security_profile'),
    path('reject/<int:student_id>/', views.reject_student, name='reject_student'),
    path('employee-own-profile/', views.employee_own_profile, name='employee-own-profile'),
     path('employee/profile/update/', views.update_employee_profile, name='update-employee-profile'),
     path('security-list', views.security_list, name='security-list'),
     path('toggle-security-status/', toggle_security_status, name='toggle_security_status'),
     
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)