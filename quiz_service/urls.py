from django.contrib import admin
from django.urls import path, include
from django.views import debug

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('quizzes/', include('quizzes.urls')),
    path('sessions/', include('quiz_sessions.urls')),
    path('stats/', include('quiz_stat.urls')),
    path('', debug.default_urlconf)
]
