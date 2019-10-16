from django.urls import path
from .views import ConsultantView, ConsultantBenchView, ConsultantProfileView, FileView

urlpatterns = [
    path('file/', FileView.as_view()),
    path('consultant/', ConsultantView.as_view()),
    path('consultant_bench/', ConsultantBenchView.as_view()),
    path('consultant_profile/', ConsultantProfileView.as_view()),
]
