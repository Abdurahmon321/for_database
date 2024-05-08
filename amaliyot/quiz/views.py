from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect
# Create your views here.
from .forms import LoginForm
from django.http import HttpResponse


def user_login(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                return redirect('after_login')
    else:
        form = LoginForm()
    return render(request, "login/login.html", {"form": form})


def after_login(request):
    if request.user.groups.filter(name="admin").exists():
        return HttpResponse("siz admin gruhidasiz ")
    elif request.user.groups.filter(name='teacher').exists():
        return HttpResponse("siz o'qituvchisiz")
    elif request.user.groups.filter(name="student").exists():
        return HttpResponse("siz o'quvchisiz")
    else:
        return HttpResponse("sizdan saytga kirish uchun ruxsat yo'q")


