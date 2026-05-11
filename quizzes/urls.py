from django.urls import path

from . import views

app_name = "quizzes"

urlpatterns = [
    path("", views.index, name="index"),
    path("my/", views.my_quizzes, name="my_quizzes"),
    path("create/", views.quiz_create, name="quiz_create"),
    path("edit/<int:quiz_id>/", views.quiz_edit, name="quiz_edit"),
    path("delete/<int:quiz_id>/", views.quiz_delete, name="quiz_delete"),
    path("publish/<int:quiz_id>/", views.quiz_publish, name="quiz_publish"),
    path('training/start/<int:quiz_id>/', views.start_training, name='start_training'),
    path('training/<int:session_id>/question/<int:question_id>/', views.training_question, name='training_question'),
]
