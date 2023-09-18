from django.urls import path, re_path
from . import views

urlpatterns = [
    path("login/", views.CustomAuthToken.as_view()),
    re_path(
        r'^users-autocomplete/$',
        views.UserAutocomplete.as_view(),
        name='users-autocomplete',
    ),
]
