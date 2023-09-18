# django imports
from rest_framework import serializers

# app imports
from .models import ClientStore


class ClientStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientStore
        fields = "__all__"
