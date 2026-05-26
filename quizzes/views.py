import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import organizer_required

from .forms import AnswerVariantFormSet, QuestionForm, QuizForm
from .models import AnswerVariant, Question, Quiz, UserAnswer
from .scoring import ScoringFactory


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
        request,
        "quizzes/quiz_form.html",
        {"form": form, "title": "Создание квиза"},
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


@organizer_required
def question_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)
    if quiz.questions.count() >= 100:
        messages.error(request, "Лимит вопросов (100) исчерпан.")
        return redirect("quizzes:quiz_edit", quiz_id=quiz.id)

    if request.method == "POST":
        form = QuestionForm(request.POST, request.FILES)
        formset = AnswerVariantFormSet(
            request.POST,
            request.FILES,
            question_type=request.POST.get("question_type"),
        )

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                question = form.save(commit=False)
                question.quiz = quiz
                question.save()
                formset.instance = question
                formset.save()
            messages.success(request, "Вопрос успешно создан.")
            return redirect("quizzes:quiz_edit", quiz_id=quiz.id)
    else:
        form = QuestionForm()
        formset = AnswerVariantFormSet(question_type="single")

    return render(
        request,
        "quizzes/question_form.html",
        {
            "form": form,
            "formset": formset,
            "quiz": quiz,
            "is_create": True,
            "title": "Новый вопрос",
        },
    )


@organizer_required
def question_edit(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)

    if request.method == "POST":
        form = QuestionForm(request.POST, request.FILES, instance=question)
        q_type = request.POST.get("question_type", question.question_type)
        formset = AnswerVariantFormSet(
            request.POST,
            request.FILES,
            instance=question,
            question_type=q_type,
        )

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, "Вопрос обновлён.")
            return redirect("quizzes:quiz_edit", quiz_id=quiz.id)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerVariantFormSet(
            instance=question,
            question_type=question.question_type,
        )

    return render(
        request,
        "quizzes/question_form.html",
        {
            "form": form,
            "formset": formset,
            "quiz": quiz,
            "question": question,
            "is_create": False,
            "title": "Редактирование",
        },
    )


@organizer_required
def question_delete(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)

    if request.method == "POST":
        with transaction.atomic():
            if quiz.status == "published" and quiz.questions.count() == 1:
                quiz.status = "draft"
                quiz.save(update_fields=["status"])
                messages.warning(request, "Квиз переведён в черновик (нет вопросов).")
            question.delete()
            messages.success(request, "Вопрос удалён.")
        return redirect("quizzes:quiz_edit", quiz_id=quiz.id)

    return render(
        request,
        "quizzes/question_confirm_delete.html",
        {"quiz": quiz, "question": question},
    )


@require_POST
@login_required
def question_reorder(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)

    data = json.loads(request.body)
    order_data = data.get("order", [])

    for item in order_data:
        Question.objects.filter(id=item["id"], quiz=quiz).update(order=item["order"])

    return JsonResponse({"status": "ok"})


@require_POST
@login_required
def answer_variant_reorder(request, question_id):
    question = get_object_or_404(Question, id=question_id, quiz__creator=request.user)

    data = json.loads(request.body)
    order_data = data.get("order", [])

    for item in order_data:
        AnswerVariant.objects.filter(id=item["id"], question=question).update(
            order=item["order"],
        )

    return JsonResponse({"status": "ok"})


@require_POST
@login_required
def submit_answer(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    try:
        data = json.loads(request.body)
        raw_answer = data.get("selected_variants")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if question.question_type == "single":
        user_answer = (
            raw_answer[0] if isinstance(raw_answer, list) and raw_answer else None
        )
        if user_answer is None:
            return JsonResponse({"error": "Выберите вариант ответа"}, status=400)

    elif question.question_type == "multiple":
        user_answer = raw_answer if isinstance(raw_answer, list) else []

    elif question.question_type == "text":
        user_answer = (
            raw_answer[0] if isinstance(raw_answer, list) and raw_answer else ""
        )
        if not user_answer or not user_answer.strip():
            return JsonResponse(
                {
                    "success": False,
                    "error": "Ответ не может быть пустым",
                    "score": 0,
                    "max_score": float(question.points),
                    "is_correct": False,
                    "percentage": 0,
                },
                status=400,
            )

    elif question.question_type == "matching":
        user_answer = raw_answer if isinstance(raw_answer, dict) else {}

    else:
        return JsonResponse({"error": "Unknown question type"}, status=400)

    strategy = ScoringFactory.get_strategy(question.question_type)
    score = strategy.calculate(question, user_answer, float(question.points))
    is_correct = score >= question.points

    UserAnswer.objects.update_or_create(
        user=request.user,
        question=question,
        defaults={
            "selected_variants": (
                user_answer
                if isinstance(user_answer, (list, dict))
                else [user_answer] if user_answer is not None else []
            ),
            "score": score,
            "is_correct": is_correct,
        },
    )

    return JsonResponse(
        {
            "success": True,
            "score": float(score),
            "max_score": float(question.points),
            "is_correct": is_correct,
            "percentage": (
                round(score / question.points * 100, 1) if question.points > 0 else 0
            ),
        },
    )
