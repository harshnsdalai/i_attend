from django.contrib import admin
from .models import User, StudentDetails,  Attendance, AttendanceRecord


admin.site.register(User)
admin.site.register(StudentDetails)
admin.site.register(Attendance)
admin.site.register(AttendanceRecord)
