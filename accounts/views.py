from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import OrganizerRegistrationForm, ParticipantRegistrationForm, CustomLoginForm


def register_organizer(request):
    if request.user.is_authenticated:
        return redirect('quizzes:my_quizzes')

    if request.method == 'POST':
        form = OrganizerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Организатор успешно зарегистрирован!')
            return redirect('quizzes:my_quizzes')
    else:
        form = OrganizerRegistrationForm()
    return render(request, 'accounts/register_organizer.html', {'form': form})


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
    return render(request, 'accounts/register_participant.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'organizer':
            return redirect('quizzes:my_quizzes')
        return redirect('quizzes:index')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            if user.role == 'organizer':
                return redirect('quizzes:my_quizzes')
            return redirect('quizzes:index')
        else:
            messages.error(request, 'Неверный логин или пароль')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})
