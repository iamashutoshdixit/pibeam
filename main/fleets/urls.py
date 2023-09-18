from django.urls import re_path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r"vehicles", views.VehicleViewSet)

urlpatterns = [] + router.urls
