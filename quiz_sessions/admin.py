from django.contrib import admin

from .models import ParticipantAnswer, ParticipantSession, QuizSession


class ParticipantAnswerInline(admin.TabularInline):
    model = ParticipantAnswer
    extra = 1
    readonly_fields = ("answered_at",)


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "unique_code", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("unique_code",)


@admin.register(ParticipantSession)
class ParticipantSessionAdmin(admin.ModelAdmin):
    list_display = ("session", "user", "participant_name", "total_score", "joined_at")
    list_filter = ("session__status",)
    search_fields = ("participant_name", "user__username")
    inlines = [ParticipantAnswerInline]


@admin.register(ParticipantAnswer)
class ParticipantAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "participant_session",
        "question",
        "is_correct",
        "points_earned",
        "answered_at",
    )
    list_filter = ("is_correct",)
    readonly_fields = ("answered_at",)
