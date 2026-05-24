import json
from .base import BaseHandler
from quizzes.models import Quiz, Question, AnswerVariant


class JSONHandler(BaseHandler):
    def export(self, quiz):
        data = {
            'quiz': {
                'title': quiz.title,
                'description': quiz.description,
                'status': quiz.status,
            },
            'questions': []
        }
        for question in quiz.questions.all().order_by('order'):
            q_data = {
                'text': question.text,
                'question_type': question.question_type,
                'points': question.points,
                'timer': question.timer,
                'order': question.order,
                'variants': []
            }
            for variant in question.answer_variants.all().order_by('order'):
                v_data = {
                    'text': variant.text,
                    'is_correct': variant.is_correct,
                    'order': variant.order,
                }
                if variant.match_left_id:
                    v_data['match_left_id'] = variant.match_left_id
                if variant.match_right_id:
                    v_data['match_right_id'] = variant.match_right_id
                q_data['variants'].append(v_data)
            data['questions'].append(q_data)
        return json.dumps(data, ensure_ascii=False, indent=2)

    def import_from_string(self, data_string, creator):
        if isinstance(data_string, bytes):
            data_string = data_string.decode('utf-8')
        data = json.loads(data_string)

        valid_types = [choice[0] for choice in Question.QUESTION_TYPE_CHOICES]

        quiz = Quiz.objects.create(
            title=data['quiz']['title'],
            description=data['quiz'].get('description', ''),
            creator=creator,
            status='draft',
        )
        for q_data in data['questions']:
            if q_data['question_type'] not in valid_types:
                raise ValueError(f"Неверный тип вопроса: {q_data['question_type']}")
            question = Question.objects.create(
                quiz=quiz,
                text=q_data['text'],
                question_type=q_data['question_type'],
                points=q_data.get('points', 1),
                timer=q_data.get('timer'),
                order=q_data.get('order', 0),
            )
            for v_data in q_data.get('variants', []):
                AnswerVariant.objects.create(
                    question=question,
                    text=v_data['text'],
                    is_correct=v_data.get('is_correct', False),
                    order=v_data.get('order', 0),
                    match_left_id=v_data.get('match_left_id'),
                    match_right_id=v_data.get('match_right_id'),
                )
        return quiz

    def validate(self, data_string):
        if isinstance(data_string, bytes):
            data_string = data_string.decode('utf-8')
        try:
            data = json.loads(data_string)
            if 'quiz' not in data or 'questions' not in data:
                return False, "Отсутствует quiz или questions"
            if 'title' not in data['quiz']:
                return False, "Отсутствует quiz.title"
            return True, "OK"
        except json.JSONDecodeError as e:
            return False, f"Ошибка парсинга JSON: {e}"
