from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import organizer_required

from .forms import QuizForm
from .models import Quiz


def index(request):
    return render(request, "index.html")


@organizer_required
def quiz_create(request):
    if request.method == "POST":
        form = QuizForm(request.POST, request.FILES)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.creator = request.user
            quiz.status = "draft"
            quiz.save()
            messages.success(request, f'Квиз "{quiz.title}" создан!')
            return redirect("quizzes:my_quizzes")
    else:
        form = QuizForm()
    return render(
        request, "quizzes/quiz_form.html", {"form": form, "title": "Создание квиза"}
    )


@organizer_required
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)

    if request.method == "POST":
        form = QuizForm(request.POST, request.FILES, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, f'Квиз "{quiz.title}" обновлён!')
            return redirect("quizzes:my_quizzes")
    else:
        form = QuizForm(instance=quiz)

    return render(
        request,
        "quizzes/quiz_form.html",
        {"form": form, "quiz": quiz, "title": "Редактирование квиза"},
    )


@organizer_required
def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)

    if request.method == "POST":
        title = quiz.title
        quiz.delete()
        messages.success(request, f'Квиз "{title}" удалён!')
        return redirect("quizzes:my_quizzes")

    return render(request, "quizzes/quiz_confirm_delete.html", {"quiz": quiz})


@organizer_required
def quiz_publish(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)

    if request.method == "POST":
        if quiz.questions.count() == 0:
            messages.error(request, "Нельзя опубликовать квиз без вопросов!")
            return redirect("quizzes:quiz_edit", quiz_id=quiz.id)

        quiz.status = "published"
        quiz.save()
        messages.success(request, f'Квиз "{quiz.title}" опубликован!')

    return redirect("quizzes:my_quizzes")


@login_required
def my_quizzes(request):
    if request.user.role != "organizer":
        return redirect("quizzes:index")

    quizzes = Quiz.objects.filter(creator=request.user).order_by("-created_at")
    paginator = Paginator(quizzes, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "quizzes/my_quizzes.html", {"quizzes": page_obj})
