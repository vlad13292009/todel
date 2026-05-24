import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import organizer_required

from .forms import AnswerVariantFormSet, QuestionForm, QuizForm
from .import_export import ImportExportFactory
from .models import AnswerVariant, Question, Quiz


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


@organizer_required
def question_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)
    if quiz.questions.count() >= 100:
        messages.error(request, "Лимит вопросов (100) исчерпан.")
        return redirect("quizzes:quiz_edit", quiz_id=quiz.id)

    if request.method == "POST":
        form = QuestionForm(request.POST, request.FILES)
        formset = AnswerVariantFormSet(
            request.POST, request.FILES, question_type=request.POST.get("question_type")
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
            request.POST, request.FILES, instance=question, question_type=q_type
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
            instance=question, question_type=question.question_type
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
            order=item["order"]
        )

    return JsonResponse({"status": "ok"})


@organizer_required
def export_quiz_json(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)
    handler = ImportExportFactory.get_handler("json")
    data = handler.export(quiz)
    from django.http import JsonResponse

    response = JsonResponse(json.loads(data), safe=False)
    response["Content-Disposition"] = f'attachment; filename="{quiz.title}.json"'
    return response


@organizer_required
def export_quiz_json(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, creator=request.user)
    handler = ImportExportFactory.get_handler("json")
    data = handler.export(quiz)
    response = HttpResponse(data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{quiz.title}.json"'
    return response


@organizer_required
def import_quiz(request):
    if request.method != 'POST':
        return redirect('quizzes:import_quiz_page')

    file = request.FILES.get('file')
    fmt = request.POST.get('format')

    if not file or fmt not in ['json', 'csv']:
        messages.error(request, 'Файл или формат не указан')
        return redirect('quizzes:import_quiz_page')

    try:
        handler = ImportExportFactory.get_handler(fmt)
        content = file.read()
        is_valid, error = handler.validate(content)
        if not is_valid:
            raise Exception(error)

        quiz = handler.import_from_string(content, request.user)
        messages.success(request, f'Квиз "{quiz.title}" успешно импортирован!')
        return redirect('quizzes:quiz_edit', quiz_id=quiz.id)

    except Exception as e:
        messages.error(request, f'Ошибка импорта: {str(e)}')
        return redirect('quizzes:import_quiz_page')


@organizer_required
def import_quiz_page(request):
    return render(request, "quizzes/import_quiz.html")
