from django.contrib import admin
from django.urls import path, include
from quizzes.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),
    path('accounts/', include('accounts.urls')),
    path('quizzes/', include('quizzes.urls')),
    path('sessions/', include('quiz_sessions.urls')),
    path('stats/', include('quiz_stat.urls')),
]
