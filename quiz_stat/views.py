from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Window
from django.db.models.functions import RowNumber
from quiz_sessions.models import QuizSession, ParticipantSession


def _serialize_answer(answer):
    return {
        'id': answer.id,
        'question_text': answer.question.text,
        'selected_answer': answer.selected_answer.text if answer.selected_answer else answer.text_answer,
        'correct_answers': list(answer.question.answer_variants.filter(is_correct=True).values_list('text', flat=True)),
        'is_correct': answer.is_correct,
        'points_earned': answer.points_earned,
        'answered_at': answer.answered_at.isoformat() if answer.answered_at else None
    }


def _serialize_participant(ps):
    return {
        'id': ps.id,
        'participant_name': ps.user.username if ps.user else ps.participant_name,
        'total_score': ps.total_score,
        'correct_answers_count': ps.correct_answers_count,
        'incorrect_answers_count': ps.incorrect_answers_count,
        'skipped_answers_count': ps.skipped_answers_count,
        'total_questions': ps.total_questions,
        'score_percent': ps.score_percent,
        'time_spent_seconds': ps.time_spent_seconds,
        'time_formatted': f"{ps.time_spent_seconds // 60}:{ps.time_spent_seconds % 60:02d}" if ps.time_spent_seconds else "0:00",
        'place_in_rating': ps.place_in_rating,
        'finished_at': ps.finished_at.isoformat() if ps.finished_at else None,
        'joined_at': ps.joined_at.isoformat()
    }


def _serialize_participant_detail(ps):
    data = _serialize_participant(ps)
    data['answers'] = [_serialize_answer(a) for a in
                       ps.answers.select_related('question', 'selected_answer').order_by('answered_at')]
    return data


class ParticipantStatsView(LoginRequiredMixin, View):
    def get(self, request, pk):
        qs = ParticipantSession.objects.select_related('session__quiz', 'user').prefetch_related(
            'answers__question', 'answers__selected_answer', 'answers__question__answer_variants'
        )
        ps = get_object_or_404(qs, pk=pk, user=request.user)
        return JsonResponse(_serialize_participant_detail(ps), safe=False)


class QuizSessionParticipantsView(LoginRequiredMixin, View):
    def get(self, request, code):
        quiz_session = get_object_or_404(QuizSession, unique_code=code)
        if request.user != quiz_session.quiz.creator and not request.user.is_staff:
            return JsonResponse({'error': 'Вы не организатор этого квиза.'}, status=403)

        qs = ParticipantSession.objects.filter(session=quiz_session).select_related('user').order_by('-total_score',
                                                                                                     'time_spent_seconds')
        qs = qs.annotate(rating_place=Window(expression=RowNumber(), order_by=[F('total_score').desc(),
                                                                               F('time_spent_seconds').asc(
                                                                                   nulls_last=True)]))

        sort_by = request.GET.get('sort')
        if sort_by == 'time':
            qs = qs.order_by('time_spent_seconds')
        elif sort_by == 'percent':
            qs = qs.order_by('-score_percent')

        results = [_serialize_participant(p) for p in qs]
        return JsonResponse({'count': len(results), 'session_code': code, 'results': results}, safe=False)
