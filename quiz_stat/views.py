from django.shortcuts import render

def update_question_stats(question, is_correct, time_taken):
    stats, created = QuestionStats.objects.get_or_create(question=question)
    stats.total_attempts += 1
    stats.total_time_spent += time_taken
    if is_correct:
        stats.correct_answers_count += 1
    stats.save()
