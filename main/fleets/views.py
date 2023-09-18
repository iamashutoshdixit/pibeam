# Django imports
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
# project imports
from fleets.serializers import VehicleSerializer

# app imports
from .models import Vehicle


class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
