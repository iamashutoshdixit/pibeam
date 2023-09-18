from django.urls import path

from . import views

urlpatterns = [
    path(r"get-config/", views.get_config),
    path(r"get-unauth-config/", views.get_unauth_config),
]
