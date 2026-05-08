from django.contrib import admin

from .models import AnswerVariant, Question, Quiz


class AnswerVariantInline(admin.TabularInline):
    model = AnswerVariant
    extra = 3


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "question_type", "points", "timer")
    list_filter = ("question_type", "quiz")
    inlines = [AnswerVariantInline]


@admin.register(AnswerVariant)
class AnswerVariantAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct")
    list_filter = ("is_correct",)
