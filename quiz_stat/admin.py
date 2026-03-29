from django.contrib import admin

from django.contrib import admin
from .models import QuestionStats

@admin.register(QuestionStats)
class QuestionStatsAdmin(admin.ModelAdmin):
    list_display = (
        'question',
        'accuracy_rate',
        'avg_response_time',
        'difficulty',
        'total_attempts'
    )
    list_sortable = ('difficulty', 'accuracy_rate')
    list_editable = ('difficulty',)
    list_filter = ('difficulty',)

    def accuracy_rate(self, obj):
        return f"{obj.accuracy_rate}%"

    accuracy_rate.admin_order_field = 'correct_answers_count'
    accuracy_rate.short_description = 'Процент успеха'
    def avg_response_time(self, obj):
        return f"{obj.avg_response_time} сек"

    avg_response_time.short_description = 'Ср. время'
