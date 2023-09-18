from rest_framework.pagination import CursorPagination


class CustomCursorPagination(CursorPagination):
    ordering = "-checkin_time"
