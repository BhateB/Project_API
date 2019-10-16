from django.urls import path
from .views import RegisterView, LoginView, LogoutView, UserList, Profile, TeamView

urlpatterns = [

    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('user_list/', UserList.as_view()),
    path('profile/', Profile.as_view()),
    path('team/', TeamView.as_view()),
]
