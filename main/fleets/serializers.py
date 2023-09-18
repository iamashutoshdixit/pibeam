# Django imports
from rest_framework import serializers

# User imports
from .models import Vehicle, Station


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = "__all__"
