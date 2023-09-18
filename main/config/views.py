# django imports

# drf imports
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.decorators import api_view, permission_classes

# app level imports
from .models import Config
from .serializers import ConfigSerializer


@api_view(["get"])
@permission_classes([IsAuthenticated])
def get_config(request):
    key = request.GET.get("key", None)
    if key is None:
        return Response({}, status=HTTP_400_BAD_REQUEST)
    queryset = Config.objects.filter(key__iexact=key)
    if queryset.count() == 0:
        return Response({}, status=HTTP_400_BAD_REQUEST)
    serializer = ConfigSerializer(queryset.first())
    return Response(serializer.data)

@api_view(["get"])
def get_unauth_config(request):
    key = request.GET.get("key", None)
    if key is None:
        return Response({}, status=HTTP_400_BAD_REQUEST)
    if "unauth_" not in key:
        return Response({}, status=HTTP_400_BAD_REQUEST)
    queryset = Config.objects.filter(key__iexact=key)
    if queryset.count() == 0:
        return Response({}, status=HTTP_400_BAD_REQUEST)
    serializer = ConfigSerializer(queryset.first())
    return Response(serializer.data)
