from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import OrganizerRegistrationForm, ParticipantRegistrationForm, CustomLoginForm


def register_organizer(request):
    if request.user.is_authenticated:
        return redirect('quizzes:index')

    if request.method == 'POST':
        form = OrganizerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Организатор успешно зарегистрирован!')
            return redirect('quizzes:index')
    else:
        form = OrganizerRegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/register_organizer.html', context)


def register_participant(request):
    if request.user.is_authenticated:
        return redirect('quizzes:index')

    if request.method == 'POST':
        form = ParticipantRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Участник успешно зарегистрирован!')
            return redirect('quizzes:index')
    else:
        form = ParticipantRegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/register_participant.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('quizzes:index')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            if user.role == 'organizer':
                return redirect('quizzes:index')
            return redirect('quizzes:index')
        else:
            messages.error(request, 'Неверный логин или пароль')
    else:
        form = CustomLoginForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/login.html', context)


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('home')


@login_required
def profile_view(request):
    context = {
        'user': request.user
    }
    return render(request, 'accounts/profile.html', context)
