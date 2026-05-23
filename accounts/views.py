from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import (
    CustomLoginForm,
    OrganizerRegistrationForm,
    ParticipantRegistrationForm,
)


def register_organizer(request):
    if request.user.is_authenticated:
        return redirect("quizzes:my_quizzes")

    if request.method == "POST":
        form = OrganizerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Организатор успешно зарегистрирован!")
            return redirect("quizzes:my_quizzes")
    else:
        form = OrganizerRegistrationForm()
    context = {
        "form": form,
        "role": "organizer",
        "title": "организатора",
        "subtitle": "Создавайте квизы и управляйте событиями",
    }
    return render(request, "accounts/register_form.html", context)


def register_participant(request):
    if request.user.is_authenticated:
        return redirect("quizzes:index")

    if request.method == "POST":
        form = ParticipantRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Участник успешно зарегистрирован!")
            return redirect("quizzes:index")
    else:
        form = ParticipantRegistrationForm()
    context = {
        "form": form,
        "role": "participant",
        "title": "участника",
        "subtitle": "Присоединяйтесь к квизам и соревнуйтесь",
    }
    return render(request, "accounts/register_form.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("quizzes:index")

    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}!")
            if user.role == "organizer":
                return redirect("quizzes:my_quizzes")
            return redirect("quizzes:index")
        messages.error(request, "Неверный логин или пароль")
    else:
        form = CustomLoginForm()

    context = {"form": form}
    return render(request, "accounts/login.html", context)


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.info(request, "Вы успешно вышли из системы.")
        return redirect("accounts:login")
    return redirect("accounts:login")


@login_required
def profile_view(request):
    context = {"user": request.user}
    return render(request, "accounts/profile.html", context)
