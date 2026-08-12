from django.contrib import admin
from .models import Teacher, Student, Batch, Department, Attendance

class TeachAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email")


@admin.register(Student)
class StudAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'email',
        'phone_no',
        'teacher',       # Added teacher column
        'batch',         # Batch is already here
        'is_active',
    )


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "date", "is_present")


admin.site.register(Teacher, TeachAdmin)
# Student already registered via @admin.register
admin.site.register(Batch)
admin.site.register(Department)
admin.site.register(Attendance, AttendanceAdmin)


