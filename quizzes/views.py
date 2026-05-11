from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse

from accounts.decorators import organizer_required

from .forms import QuizForm
from .models import TrainingSession, TrainingProgress, Question, AnswerVariant, Quiz


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


@login_required
def start_training(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, status="published")
    session = TrainingSession.objects.create(user=request.user, quiz=quiz)
    question = quiz.questions.first()
    return redirect("quizzes:training_question", session_id=session.id, question_id=question.id)


@login_required
def training_question(request, session_id, question_id):
    session = get_object_or_404(TrainingSession, id=session_id, user=request.user)
    question = get_object_or_404(Question, id=question_id, quiz=session.quiz)

    user_answer = TrainingProgress.objects.filter(session=session, question=question).first()
    context = {
        "session": session,
        "question": question,
        "all_questions": session.quiz.questions.all(),
        "user_answer": user_answer,
    }

    if request.method == "POST":
        selected_ids = request.POST.getlist("variants")
        if not selected_ids:
            messages.warning(request, "Выберите хотя бы один вариант.")
            return render(request, "quizzes/training_mode.html", context)

        correct_ids = list(question.answer_variants.filter(is_correct=True).values_list("id", flat=True))
        is_correct = set(map(int, selected_ids)) == set(correct_ids)

        progress, _ = TrainingProgress.objects.update_or_create(
            session=session,
            question=question,
            defaults={"is_correct": is_correct}
        )
        progress.selected_variants.set(selected_ids)

        context["user_answer"] = progress
        context["is_correct_now"] = is_correct
        context["correct_ids"] = correct_ids

    return render(request, "quizzes/training_mode.html", context)
