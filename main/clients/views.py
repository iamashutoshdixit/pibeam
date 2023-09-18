# django imports
from rest_framework import viewsets
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


# app imports
from .serializers import ClientStoreSerializer
from .models import ClientStore


class ClientStoreViewSet(viewsets.ModelViewSet):
    queryset = ClientStore.objects.all()
    serializer_class = ClientStoreSerializer

    http_method_names = ["get"]

    @method_decorator(cache_page(60 * 60 * 1))
    def list(self, request):
        return Response([])

    def retrieve(self, request, pk=None):
        obj = self.queryset.filter(pk=pk).first()
        serializer = self.serializer_class(obj)
        return Response(serializer.data)
