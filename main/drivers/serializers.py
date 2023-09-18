# Django imports
from rest_framework import serializers

# User Imports
from fleets.serializers import VehicleSerializer, StationSerializer

from .models import (
    Onboarding,
    Driver,
    DriverLocations,
    DriverContract,
)
from .helpers import driver_age_validator


class OnboardingSerializer(serializers.ModelSerializer):
    def validate_dob(self, date):
        return driver_age_validator(date)

    class Meta:
        model = Onboarding
        fields = "__all__"


class DriverSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    dob = serializers.ReadOnlyField()
    mobile_no = serializers.ReadOnlyField()
    house_no = serializers.ReadOnlyField()
    street = serializers.ReadOnlyField()
    locality = serializers.ReadOnlyField()
    city = serializers.ReadOnlyField()
    pincode = serializers.ReadOnlyField()
    own_house = serializers.ReadOnlyField()
    aadhar_number = serializers.ReadOnlyField()
    pan_number = serializers.ReadOnlyField()
    account_number = serializers.ReadOnlyField()
    account_name = serializers.ReadOnlyField()
    ifsc_code = serializers.ReadOnlyField()
    class Meta:
        model = Driver
        fields = "__all__"


class DriverLocationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLocations
        fields = "__all__"


class DriverContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverContract
        fields = "__all__"
