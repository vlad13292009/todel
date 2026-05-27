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
    path("export/<int:quiz_id>/json/", views.export_quiz_json, name="export_quiz_json"),
    path("export/<int:quiz_id>/csv/", views.export_quiz_csv, name="export_quiz_csv"),
    path("import/", views.import_quiz, name="import_quiz"),
    path("import/page/", views.import_quiz_page, name="import_quiz_page"),
    path(
        "quiz/<int:quiz_id>/question/create/",
        views.question_create,
        name="question_create",
    ),
    path(
        "quiz/<int:quiz_id>/question/<int:question_id>/edit/",
        views.question_edit,
        name="question_edit",
    ),
    path(
        "quiz/<int:quiz_id>/question/<int:question_id>/delete/",
        views.question_delete,
        name="question_delete",
    ),
    path(
        "quiz/<int:quiz_id>/questions/reorder/",
        views.question_reorder,
        name="question_reorder",
    ),
    path(
        "question/<int:question_id>/variants/reorder/",
        views.answer_variant_reorder,
        name="answer_variant_reorder",
    ),
]
