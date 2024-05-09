from django.shortcuts import render, redirect, reverse
from . import forms, models
from django.db.models import Sum
from django.contrib.auth.models import Group, User
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from datetime import date, timedelta
from quiz import models as QMODEL
from student import models as SMODEL
from quiz import forms as QFORM


# for showing signup/login button for teacher


def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()


@login_required(login_url='user_login')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    dict = {

        'total_course': QMODEL.Course.objects.all().count(),
        'total_question': QMODEL.Question.objects.all().count(),
        'total_student': SMODEL.Student.objects.all().count()
    }
    return render(request, 'teacher/teacher_dashboard.html', context=dict)


@login_required(login_url='user_login')
@user_passes_test(is_teacher)
def teacher_exam_view(request):
    return render(request, 'teacher/teacher_exam.html')


@login_required(login_url='user_login')
@user_passes_test(is_teacher)
def teacher_add_exam_view(request):
    courseForm = QFORM.CourseForm()
    if request.method == 'POST':
        courseForm = QFORM.CourseForm(request.POST)
        if courseForm.is_valid():
            courseForm.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-exam')
    return render(request, 'teacher/teacher_add_exam.html', {'courseForm': courseForm})


@login_required(login_url='user_login')
@user_passes_test(is_teacher)
def teacher_view_exam_view(request):
    courses = QMODEL.Course.objects.all()
    return render(request, 'teacher/teacher_view_exam.html', {'courses': courses})


@login_required(login_url='user_login')
@user_passes_test(is_teacher)
def delete_exam_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/teacher/teacher-view-exam')


@login_required(login_url='adminlogin')
def teacher_question_view(request):
    return render(request, 'teacher/teacher_question.html')


@login_required(login_url='user_login')
@user_passes_test(is_teacher)
def teacher_add_question_view(request):
    questionForm = QFORM.QuestionForm()
    if request.method == 'POST':
        questionForm = QFORM.QuestionForm(request.POST)
        if questionForm.is_valid():
            question = questionForm.save(commit=False)
            course = QMODEL.Course.objects.get(id=request.POST.get('courseID'))
            author = User.objects.get(id=request.user.id)
            question.author = author
            question.course = course
            question.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-question')
    return render(request, 'teacher/teacher_add_question.html', {'questionForm': questionForm})


@login_required(login_url='user_login')
@user_passes_test(is_teacher)
def teacher_view_question_view(request):
    courses = QMODEL.Course.objects.all()
    return render(request, 'teacher/teacher_view_question.html', {'courses': courses})


@login_required(login_url='user_login')
@user_passes_test(is_teacher)
def see_question_view(request, pk):
    questions = QMODEL.Question.objects.all().filter(course_id=pk)
    return render(request, 'teacher/see_question.html', {'questions': questions})


@login_required(login_url='user_login')
@user_passes_test(is_teacher)
def remove_question_view(request, pk):
    question = QMODEL.Question.objects.get(id=pk)
    if request.user == question.author:
        question.delete()
        return HttpResponseRedirect('/teacher/teacher-view-question')
    return HttpResponseRedirect('/teacher/teacher-view-question')


@login_required(login_url='user-login')
@user_passes_test(is_teacher)
def update_question(request, pk):
    question = QMODEL.Question.objects.get(pk=pk)
    if request.method == 'POST':
        form = QFORM.QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('teacher-question')  # O'zgartirilgan savolni ro'yxatga qaytarish
    else:
        form = QFORM.QuestionForm(instance=question)

    return render(request, 'teacher/teacher_update_question.html', {'form': form})