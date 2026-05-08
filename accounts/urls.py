from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("register_organizer/", views.register_organizer, name="register_organizer"),
    path(
        "register_participant/", views.register_participant, name="register_participant"
    ),
]
