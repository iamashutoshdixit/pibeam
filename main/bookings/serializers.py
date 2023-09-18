# django imports
from rest_framework import serializers

# project imports
from fleets.serializers import (
    VehicleSerializer,
    StationSerializer,
)

# app imports
from .models import Trip, Roster


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = "__all__"


class RosterSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer()
    destination_station = StationSerializer()

    class Meta:
        model = Roster
        fields = "__all__"
