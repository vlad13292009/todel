from django.shortcuts import render


def index(request):
    return render(request, 'index.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Question, QuestionTemplate
from .forms import QuestionForm
from django.contrib.auth.decorators import login_required


@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if request.method == 'POST':
        if 'save_to_library' in request.POST:
            try:
                template = QuestionTemplate.objects.create(
                    text=question.text,
                    answer_type=question.answer_type,
                    options=question.options,
                    correct_answer=question.correct_answer,
                    created_by=request.user,
                    is_public=False
                )

                return redirect(reverse('my_question_library'))
            except Exception as e:
                messages.error(request, f"Ошибка сохранения в библиотеку: {e}")
                return redirect(reverse('edit_question', kwargs={'question_id': question_id}))

        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect(reverse('quiz_detail', kwargs={'pk': question.quiz_id}))
    else:
        form = QuestionForm(instance=question)

    context = {
        'question': question,
        'form': form,
    }
    return render(request, 'quizzes/edit_question.html', context)


from django.shortcuts import render, redirect
from django.urls import reverse
from .models import QuestionTemplate
from django.contrib.auth.decorators import login_required
from django.db.models import Q


@login_required
def my_question_library(request):
    user = request.user

    queryset = QuestionTemplate.objects.filter(created_by=user)

    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(text__icontains=query) |
            Q(options__icontains=query)
        )

    filter_answer_type = request.GET.get('answer_type')
    if filter_answer_type:
        queryset = queryset.filter(answer_type=filter_answer_type)

    filter_public = request.GET.get('public')
    if filter_public == 'true':
        queryset = queryset.filter(is_public=True)
    elif filter_public == 'false':
        queryset = queryset.filter(is_public=False)

    sort_by = request.GET.get('sort_by', '-created_at')
    if sort_by in ['created_at', '-created_at', 'text', '-text', 'answer_type', '-answer_type']:
        queryset = queryset.order_by(sort_by)

    context = {
        'templates': queryset,
        'answer_type_choices': QuestionTemplate.ANSWER_TYPE_CHOICES,
        'current_query': query,
        'current_filter_answer_type': filter_answer_type,
        'current_filter_public': filter_public,
        'current_sort_by': sort_by,
    }
    return render(request, 'quizzes/my_library.html', context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import QuestionTemplate, Question, Quiz
from django.shortcuts import get_object_or_404

@login_required
@csrf_exempt
@require_POST
def add_template_to_quiz(request):
    template_id = request.POST.get('template_id')
    quiz_id = request.POST.get('quiz_id')

    if not template_id or not quiz_id:
        return JsonResponse({'success': False, 'message': 'Не указан ID шаблона или квиза.'}, status=400)

    try:
        template = QuestionTemplate.objects.get(pk=template_id)
        quiz = Quiz.objects.get(pk=quiz_id, owner=request.user)

        new_question = Question.objects.create(
            quiz=quiz,
            text=template.text,
            answer_type=template.answer_type,
            options=template.options,
            correct_answer=template.correct_answer,
        )

        return JsonResponse({'success': True, 'message': 'Вопрос успешно добавлен в квиз.'})

    except QuestionTemplate.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Шаблон вопроса не найден.'}, status=404)
    except Quiz.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Квиз не найден или не принадлежит вам.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Произошла ошибка: {e}'}, status=500)

from django.http import JsonResponse

@login_required
def get_user_quizzes(request):
    quizzes = Quiz.objects.filter(owner=request.user).values('id', 'title')
    return JsonResponse(list(quizzes), safe=False)
