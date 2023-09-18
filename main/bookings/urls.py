from rest_framework import routers
from . import views


router = routers.DefaultRouter()

router.register(r"rosters", views.RosterViewSet)
router.register(r"trips", views.TripViewSet)

urlpatterns = [] + router.urls
