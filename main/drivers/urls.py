# django imports
from django.urls import path
from rest_framework import routers

# app imports
from . import views

router = routers.DefaultRouter()
router.register(r"onboardings", views.OnboardingViewSet)
router.register(r"drivers", views.DriverViewSet)
router.register(r"contracts", views.DriverContractViewSet)

urlpatterns = [
    path("s3-upload/", views.GetUploadURL.as_view()),
    path("generate-otp/", views.send_otp),
    path("submit-otp/", views.submit_otp),
] + router.urls
