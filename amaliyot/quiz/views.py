from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, reverse
from . import forms, models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.conf import settings
from datetime import date, timedelta
from django.db.models import Q
from django.core.mail import send_mail
from teacher import models as TMODEL
from student import models as SMODEL
from teacher import forms as TFORM
from student import forms as SFORM
from quiz import forms as QFROM
from quiz import models as QMODEL
from django.contrib.auth.models import User


def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'quiz/index.html')


def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()


def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

def is_admin(user):
    return user.groups.filter(name='TEACHER').exists()


def user_login(request):
    if request.method == "POST":
        form = QFROM.LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('afterlogin')
    else:
        form = QFROM.LoginForm()
    return render(request, "quiz/adminlogin.html", context={"form": form})


def user_logout(request):
    logout(request)
    return redirect("user_login")

def add_teacher(request):
    if request.method == "POST":
        form = QFROM.UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            teacher = TMODEL.Teacher.objects.create(user=user)
            # Assign the user to the TEACHER group
            teacher_group = Group.objects.get(name='TEACHER')
            user.groups.add(teacher_group)

            return redirect("admin-dashboard")

    else:
        form = QFROM.UserSignupForm()

    return render(request, "quiz/add_teacher.html", {"form": form})


def add_student(request):
    if request.method == "POST":
        form = QFROM.UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            student = SMODEL.Student.objects.create(user=user)
            # Assign the user to the TEACHER group
            student_group = Group.objects.get(name='STUDENT')
            user.groups.add(student_group)

            return redirect("admin-dashboard")

    else:
        form = QFROM.UserSignupForm()

    return render(request, "quiz/add_student.html", {"form": form})

def afterlogin_view(request):
    if is_student(request.user):
        return redirect('student/student-dashboard')

    elif is_teacher(request.user):
        accountapproval = TMODEL.Teacher.objects.all().filter(user_id=request.user.id, status=True)
        if accountapproval:
            return redirect('teacher/teacher-dashboard')
        else:
            return render(request, 'teacher/teacher_wait_for_approval.html')
    else:
        return redirect('admin-dashboard')


def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('user_login')


@login_required(login_url='user_login')
def admin_dashboard_view(request):
    dict = {
        'total_student': SMODEL.Student.objects.all().count(),
        'total_teacher': TMODEL.Teacher.objects.all().count(),
        'total_course': models.Course.objects.all().count(),
        'total_question': models.Question.objects.all().count(),
    }
    return render(request, 'quiz/admin_dashboard.html', context=dict)


@login_required(login_url='user_login')
def admin_teacher_view(request):
    dict = {
        'total_teacher': TMODEL.Teacher.objects.all().filter(status=True).count(),
        'pending_teacher': TMODEL.Teacher.objects.all().filter(status=False).count(),
        'salary': TMODEL.Teacher.objects.all().filter(status=True).aggregate(Sum('salary'))['salary__sum'],
    }
    return render(request, 'quiz/admin_teacher.html', context=dict)


@login_required(login_url='user_login')
def admin_view_teacher_view(request):
    teachers = TMODEL.Teacher.objects.all().filter(status=True)
    return render(request, 'quiz/admin_view_teacher.html', {'teachers': teachers})


@login_required(login_url='user_login')
def update_teacher_view(request, pk):
    teacher = TMODEL.Teacher.objects.get(id=pk)
    user = TMODEL.User.objects.get(id=teacher.user_id)
    if request.method == 'POST':
        userForm = TFORM.TeacherUserForm(request.POST, instance=user)
        teacherForm = TFORM.TeacherForm(request.POST, request.FILES, instance=teacher)
        if userForm.is_valid() and teacherForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(user.password)
            user.save()
            teacherForm.save()
            return redirect('admin-view-teacher')
    else:
        userForm = TFORM.TeacherUserForm(instance=user)
        teacherForm = TFORM.TeacherForm(instance=teacher)

    mydict = {'userForm': userForm, 'teacherForm': teacherForm}
    return render(request, 'quiz/update_teacher.html', context=mydict)


@login_required(login_url='user_login')
def delete_teacher_view(request, pk):
    teacher = TMODEL.Teacher.objects.get(id=pk)
    user = User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect('/admin-view-teacher')


@login_required(login_url='user_login')
def admin_view_teacher_salary_view(request):
    teachers = TMODEL.Teacher.objects.all().filter(status=True)
    return render(request, 'quiz/admin_view_teacher_salary.html', {'teachers': teachers})


@login_required(login_url='user_login')
def admin_student_view(request):
    dict = {
        'total_student': SMODEL.Student.objects.all().count(),
    }
    return render(request, 'quiz/admin_student.html', context=dict)


@login_required(login_url='user_login')
def admin_view_student_view(request):
    students = SMODEL.Student.objects.all()
    return render(request, 'quiz/admin_view_student.html', {'students': students})


@login_required(login_url='user_login')
def update_student_view(request, pk):
    student = SMODEL.Student.objects.get(id=pk)
    user = SMODEL.User.objects.get(id=student.user_id)
    userForm = SFORM.StudentUserForm(instance=user)
    studentForm = SFORM.StudentForm(request.FILES, instance=student)
    mydict = {'userForm': userForm, 'studentForm': studentForm}
    if request.method == 'POST':
        userForm = SFORM.StudentUserForm(request.POST, instance=user)
        studentForm = SFORM.StudentForm(request.POST, request.FILES, instance=student)
        if userForm.is_valid() and studentForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            studentForm.save()
            return redirect('admin-view-student')
    return render(request, 'quiz/update_student.html', context=mydict)


@login_required(login_url='user_login')
def delete_student_view(request, pk):
    student = SMODEL.Student.objects.get(id=pk)
    user = User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return HttpResponseRedirect('/admin-view-student')


@login_required(login_url='user_login')
def admin_course_view(request):
    return render(request, 'quiz/admin_course.html')


@login_required(login_url='user_login')
def admin_add_course_view(request):
    courseForm = forms.CourseForm()
    if request.method == 'POST':
        courseForm = forms.CourseForm(request.POST)
        if courseForm.is_valid():
            courseForm.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-course')
    return render(request, 'quiz/admin_add_course.html', {'courseForm': courseForm})


@login_required(login_url='user_login')
def admin_view_course_view(request):
    courses = models.Course.objects.all()
    return render(request, 'quiz/admin_view_course.html', {'courses': courses})


@login_required(login_url='user_login')
def delete_course_view(request, pk):
    course = models.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/admin-view-course')


@login_required(login_url='user_login')
def admin_question_view(request):
    return render(request, 'quiz/admin_question.html')


@login_required(login_url='user_login')
def admin_add_question_view(request):
    questionForm = forms.QuestionForm()
    if request.method == 'POST':
        questionForm = forms.QuestionForm(request.POST)
        if questionForm.is_valid():
            question = questionForm.save(commit=False)
            course = models.Course.objects.get(id=request.POST.get('courseID'))
            question.course = course
            question.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-question')
    return render(request, 'quiz/admin_add_question.html', {'questionForm': questionForm})


@login_required(login_url='user_login')
def admin_view_question_view(request):
    courses = models.Course.objects.all()
    return render(request, 'quiz/admin_view_question.html', {'courses': courses})


@login_required(login_url='user_login')
def view_question_view(request, pk):
    questions = models.Question.objects.all().filter(course_id=pk)
    return render(request, 'quiz/view_question.html', {'questions': questions})


@login_required(login_url='user_login')
def delete_question_view(request, pk):
    question = models.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/admin-view-question')

@login_required(login_url='user-login')
def update_question(request, pk):
    question = QMODEL.Question.objects.get(pk=pk)
    if request.user == question.author:
        if request.method == 'POST':
            form = QFROM.QuestionForm(request.POST, instance=question)
            if form.is_valid():
                form.save()
                return redirect('teacher-question')  # O'zgartirilgan savolni ro'yxatga qaytarish
        else:
            form = QFROM.QuestionForm(instance=question)

        return render(request, 'teacher/teacher_update_question.html', {'form': form})
    return redirect('admin-view-question')

@login_required(login_url='user_login')
def admin_view_student_marks_view(request):
    students = SMODEL.Student.objects.all()
    return render(request, 'quiz/admin_view_student_marks.html', {'students': students})


@login_required(login_url='user_login')
def admin_view_marks_view(request, pk):
    courses = models.Course.objects.all()
    response = render(request, 'quiz/admin_view_marks.html', {'courses': courses})
    response.set_cookie('student_id', str(pk))
    return response


@login_required(login_url='user_login')
def admin_check_marks_view(request, pk):
    course = models.Course.objects.get(id=pk)
    student_id = request.COOKIES.get('student_id')
    student = SMODEL.Student.objects.get(id=student_id)

    results = models.Result.objects.all().filter(exam=course).filter(student=student)
    return render(request, 'quiz/admin_check_marks.html', {'results': results})


def handler404(request, exception, template_name="404.html"):
    response = render(request, template_name)
    response.status_code = 404
    return response

