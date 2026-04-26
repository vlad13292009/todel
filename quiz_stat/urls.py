from django.urls import path
from .views import ParticipantStatsView, QuizSessionParticipantsView

app_name = 'quiz_stat'

urlpatterns = [
    path('api/stats/my/<int:pk>/', ParticipantStatsView.as_view(), name='participant_stats_api'),
    path('api/stats/session/<str:code>/participants/', QuizSessionParticipantsView.as_view(),
         name='session_participants_api'),
]
