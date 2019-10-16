from django.urls import path
from .views import CitiesView, DiscordSendMessage

urlpatterns = [

    path('cities/', CitiesView.as_view()),
    path('webhook/discord/',DiscordSendMessage.as_view())
]
