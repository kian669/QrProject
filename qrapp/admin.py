from django.contrib import admin
from .models import Student
from .models import Security
from .models import Violation
from .models import StudentMasterList
from .models import Logs
from .models import Vehicle, Employee, EmployeeVehicle,EmployeeViolation, EmployeeNotification,EmployeePendingRegistration, EmployeeLogs
# Register your models here.

admin.site.register(Student)
admin.site.register(Security)
admin.site.register(Violation)
admin.site.register(StudentMasterList)
admin.site.register(Logs)
admin.site.register(Vehicle)
admin.site.register(Employee)
admin.site.register(EmployeeVehicle)
admin.site.register(EmployeeViolation)
admin.site.register(EmployeeNotification)
admin.site.register(EmployeePendingRegistration)
admin.site.register(EmployeeLogs)
