# drf imports
from rest_framework import serializers

# app level imports
from .models import Config


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config
        fields = ["key", "value"]
