from django.contrib import admin
from django.urls import path, include
from quizzes.views import index
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),
    path('accounts/', include('accounts.urls')),
    path('quizzes/', include('quizzes.urls')),
    path('sessions/', include('quiz_sessions.urls')),
    path('stats/', include('quiz_stat.urls')),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('contacts/', TemplateView.as_view(template_name='contacts.html'), name='contacts'),
    path('rules/', TemplateView.as_view(template_name='rules.html'), name='rules')
]
