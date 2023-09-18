# python imports
from datetime import datetime

# django imports
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

# project imports
from fleets.models import Vehicle
from config.models import Config
from libs.paginations import CustomCursorPagination
from bookings.constants import TRIP_NOT_FOUND
from libs.constants import INVALID_DATA
from drivers.models import Driver

# app imports
from .models import Trip, Roster
from .serializers import TripSerializer, RosterSerializer
from .constants import (
    PREVIOUS_TRIP_ACTIVE,
    ROSTER_NOT_ASSIGNED,
    ROSTER_TRIP_COMPLETED_ALREADY,
    TRIP_START_TIME_DELTA,
    TRIP_CANNOT_START,
    TRIP_INVALID_ACTION,
    TRIP_VEHICLE_NOT_ASSIGNED,
)


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch"]
    pagination_class = CustomCursorPagination

    def list(self, request):
        qs = self.queryset
        serializer = TripSerializer(qs, many=True)
        return Response(serializer.data)

    # start_ride creates the trip object
    # check_in add the in_latitude, in_longitude, in_time
    # check_out add the out_latitude, out_longitude, out_time
    # end_ride add the end ride time, end ride km and trip sheet photo
    @action(methods=['POST'], detail=False, url_path='start-ride')
    def start_ride(self, request):
        start_time = datetime.now()
        try:
            driver = Driver.objects.get(onboarding__mobile_no=request.user.username)
            roster = Roster.objects.get(id=int(request.data["roster"]))
            start_km = float(int(request.data["start_km"]))
            vehicle_photos = request.data.get("vehicle_photos", [])
        except (KeyError, Roster.DoesNotExist, Driver.DoesNotExist):
            return Response(
                INVALID_DATA,
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if roster.driver != driver:
            return Response(
                ROSTER_NOT_ASSIGNED,
                status=status.HTTP_403_FORBIDDEN,
            )
        
        if roster.vehicle is None:
            return Response(
                TRIP_VEHICLE_NOT_ASSIGNED,
                status=status.HTTP_403_FORBIDDEN,
            )

        # roster_start_time validation
        roster_start_time = roster.slot_start_time
        roster_start_time = datetime(
            year=start_time.year,
            month=start_time.month,
            day=start_time.day,
            hour=roster_start_time.hour,
            minute=roster_start_time.minute,
            second=roster_start_time.second,
        )
        roster_start_delta = Config.get_value("roster_start_ride") or TRIP_START_TIME_DELTA
        if start_time <= roster_start_time:
            if (roster_start_time - start_time).seconds / 60 > roster_start_delta:
                return Response(
                    TRIP_CANNOT_START,
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # check if there's an active trip
        past_active_trips = Trip.objects.filter(
            is_active=True,
            roster=roster,
        )
        if past_active_trips.count() > 0:
            return Response(
                PREVIOUS_TRIP_ACTIVE,
                status=status.HTTP_403_FORBIDDEN,
            )

        # check if a trip for the roster was created earlier for the day
        # date today at 00:00:00
        dt = datetime.now()
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        roster_trip_today = Trip.objects.filter(
            roster=roster,
            created_at__gte=dt,
        )
        if roster_trip_today.count() > 0:
            return Response(
                ROSTER_TRIP_COMPLETED_ALREADY,
                status=status.HTTP_400_BAD_REQUEST,
            )

        # create the trip object
        trip = Trip(
            roster=roster,
            start_km=start_km,
            status=Trip.STATUS.RIDE_STARTED,
            vehicle_photos=vehicle_photos,
            is_active=True,
        )

        trip.save()
        serializer = TripSerializer(trip)
        return Response(serializer.data)


    @action(methods=['POST'], detail=True, url_path='check-in')
    def check_in(self, request, *args, **kwargs):
        trip = self.get_object()
        if trip is None:
            return Response(
                TRIP_NOT_FOUND,
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            in_latitude = request.data["in_latitude"]
            in_longitude = request.data["in_longitude"]
        except KeyError:
            return Response(
                INVALID_DATA,
                status=status.HTTP_400_BAD_REQUEST,
            )
        if trip.status != Trip.STATUS.RIDE_STARTED:
            return Response(
                TRIP_INVALID_ACTION,
                status=status.HTTP_400_BAD_REQUEST,
            )
        trip.in_latitude = in_latitude
        trip.in_longitude = in_longitude
        trip.checkin_time = datetime.now()
        trip.status = Trip.STATUS.CHECK_IN
        trip.save()
        serializer = TripSerializer(trip)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True, url_path='check-out')
    def check_out(self, request, *args, **kwargs):
        trip = self.get_object()
        try:
            out_latitude = request.data["out_latitude"]
            out_longitude = request.data["out_longitude"]
        except KeyError:
            return Response(
                INVALID_DATA,
                status=status.HTTP_400_BAD_REQUEST,
            )
        if trip is None:
            return Response(
                TRIP_NOT_FOUND,
                status=status.HTTP_400_BAD_REQUEST,
            )
        if trip.status != Trip.STATUS.CHECK_IN:
            return Response(
                TRIP_INVALID_ACTION,
                status=status.HTTP_400_BAD_REQUEST,
            )
        trip.out_latitude = out_latitude
        trip.out_longitude = out_longitude
        trip.checkout_time = datetime.now()
        trip.status = Trip.STATUS.CHECK_OUT
        trip.save()
        serializer = TripSerializer(trip)
        return Response(serializer.data)


    @action(methods=['POST'], detail=True, url_path='end-ride')
    def end_ride(self, request, *args, **kwargs):
        try:
            trip = self.get_object()
            if trip is None:
                raise Trip.DoesNotExist
            trip_sheet_photo = request.data["trip_sheet_photo"]
            end_km = float(int(request.data["end_km"]))
        except (KeyError, Trip.DoesNotExist):
            return Response(
                INVALID_DATA,
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # update the trip object
        trip.end_km = end_km
        trip.status = Trip.STATUS.RIDE_COMPLETED
        trip.ended_at = datetime.now()
        trip.trip_sheet_photo = trip_sheet_photo
        trip.is_active = False
        trip.save()

        serializer = TripSerializer(trip)
        return Response(serializer.data)


class RosterViewSet(viewsets.ModelViewSet):
    queryset = Roster.objects.filter(is_active=True)
    serializer_class = RosterSerializer
    lookup_field = "id"
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]

    def list(self, request):
        qs = self.queryset.filter(driver__onboarding__mobile_no=request.user.username)
        serializer = RosterSerializer(qs, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=True, url_path='trip')
    def trip(self, request, *args, **kwargs):
        """
        This api will return the active trips associated with the roster
        """
        roster = self.get_object()
        data = {}
        qs = Trip.objects.filter(roster=roster, is_active=True).last()
        if qs is not None:
            data = TripSerializer(qs).data
        return Response(data)
        

