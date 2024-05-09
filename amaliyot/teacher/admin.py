from django.contrib import admin
from teacher.models import Teacher
# Register your models here.


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'mobile', 'status', 'salary')