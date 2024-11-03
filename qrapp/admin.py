from django.contrib import admin
from .models import Student
from .models import Security
from .models import Violation
from .models import StudentMasterList
from .models import Logs
# Register your models here.

admin.site.register(Student)
admin.site.register(Security)
admin.site.register(Violation)
admin.site.register(StudentMasterList)
admin.site.register(Logs)