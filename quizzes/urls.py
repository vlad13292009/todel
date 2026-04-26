from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('', views.index, name='index'),
    path('my-library/', views.my_question_library, name='my_question_library'),
]
