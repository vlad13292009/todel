import pandas as pd
from io import StringIO
from .base import BaseHandler
from quizzes.models import Quiz, Question, AnswerVariant


class CSVHandler(BaseHandler):
    def export(self, quiz):
        rows = []
        for question in quiz.questions.all().order_by('order'):
            for variant in question.answer_variants.all().order_by('order'):
                rows.append({
                    'quiz_title': quiz.title,
                    'quiz_description': quiz.description,
                    'question_text': question.text,
                    'question_type': question.question_type,
                    'question_points': question.points,
                    'question_timer': question.timer or '',
                    'variant_text': variant.text,
                    'variant_is_correct': variant.is_correct,
                    'variant_order': variant.order,
                    'match_left_id': variant.match_left_id or '',
                    'match_right_id': variant.match_right_id or '',
                })
        df = pd.DataFrame(rows)
        out = StringIO()
        df.to_csv(out, index=False, encoding='utf-8-sig')
        return out.getvalue()

    def import_from_string(self, data_string, creator):
        if isinstance(data_string, bytes):
            data_string = data_string.decode('utf-8-sig')
        df = pd.read_csv(StringIO(data_string))
        return self._import_from_df(df, creator)

    def _import_from_df(self, df, creator):
        quiz = Quiz.objects.create(
            title=df.iloc[0]['quiz_title'],
            description=df.iloc[0].get('quiz_description', ''),
            creator=creator,
            status='draft',
        )
        questions_data = []
        current_text = None
        for _, row in df.iterrows():
            if current_text != row['question_text']:
                current_text = row['question_text']
                questions_data.append({
                    'text': row['question_text'],
                    'question_type': row['question_type'],
                    'points': row['question_points'],
                    'timer': row['question_timer'] if pd.notna(row['question_timer']) else None,
                    'variants': [],
                })
            questions_data[-1]['variants'].append({
                'text': row['variant_text'],
                'is_correct': row['variant_is_correct'],
                'order': row['variant_order'],
                'match_left_id': row.get('match_left_id') if pd.notna(row.get('match_left_id')) else None,
                'match_right_id': row.get('match_right_id') if pd.notna(row.get('match_right_id')) else None,
            })
        for qd in questions_data:
            q = Question.objects.create(
                quiz=quiz,
                text=qd['text'],
                question_type=qd['question_type'],
                points=qd['points'],
                timer=qd['timer'],
            )
            for vd in qd['variants']:
                AnswerVariant.objects.create(question=q, **vd)
        return quiz

    def validate(self, data_string):
        if isinstance(data_string, bytes):
            data_string = data_string.decode('utf-8-sig')
        try:
            df = pd.read_csv(StringIO(data_string))
            required = ['quiz_title', 'question_text', 'question_type', 'variant_text', 'variant_is_correct']
            for col in required:
                if col not in df.columns:
                    return False, f"Нет колонки: {col}"
            if df.empty:
                return False, "Файл пуст"
            return True, "OK"
        except Exception as e:
            return False, f"Ошибка чтения CSV: {e}"
