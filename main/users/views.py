# Django imports
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from dal import autocomplete
# User imports
from drivers.models import Driver
from drivers.serializers import DriverSerializer
from .constants import USER_INACTIVE
from .models import User


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid() is False:
            return Response(
                USER_INACTIVE,
                status=status.HTTP_403_FORBIDDEN,
            )
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        driver = Driver.objects.select_related('user').filter(id=user.id).first()
        if driver:
            if driver.is_active is False:
                return Response(
                    USER_INACTIVE,
                    status=status.HTTP_403_FORBIDDEN,
                )
            driver_serializer = DriverSerializer(driver)
            return Response(
                {
                    "token": token.key,
                    "user_id": user.pk,
                    "username": user.username,
                    "driver": driver_serializer.data,
                }
            )
        else:
            return Response(
                {
                    "token": token.key,
                    "user_id": user.pk,
                    "username": user.username,
                }
            )


class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return User.objects.none()

        qs = User.objects.filter(is_active=True)
        if self.q:
            qs = qs.filter(username__istartswith=self.q)

        return qs