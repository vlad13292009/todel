from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/quizzes/", permanent=False)),
    path("accounts/", include("accounts.urls")),
    path("quizzes/", include("quizzes.urls")),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about"),
    path(
        "contacts/",
        TemplateView.as_view(template_name="contacts.html"),
        name="contacts",
    ),
    path("rules/", TemplateView.as_view(template_name="rules.html"), name="rules"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
