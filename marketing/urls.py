from django.urls import path
from .views import VendorView, LeadView, SubmissionView, ScreeningView, CompanyView, CalendarInterviews, \
    Suggestions

urlpatterns = [

    path('vendor/', VendorView.as_view()),
    path('lead/', LeadView.as_view()),
    path('submission/', SubmissionView.as_view()),
    path('screening/', ScreeningView.as_view()),
    path('company/', CompanyView.as_view()),
    path('cal_interviews/', CalendarInterviews.as_view()),
    path('suggestions/', Suggestions.as_view()),
    # path('counter/', DataCounts.as_view()),
]
