# django imports
from rest_framework import routers

# app imports
from . import views

router = routers.DefaultRouter()
router.register(r"client-stores", views.ClientStoreViewSet)

urlpatterns = [] + router.urls
