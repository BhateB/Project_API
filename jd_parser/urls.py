from django.urls import path
from .views import JobAndSkillExtraction

urlpatterns = [
    path('parser/', JobAndSkillExtraction.as_view()),
]
