from django.contrib import admin
from student.models import Student
# Register your models here.


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'mobile')
