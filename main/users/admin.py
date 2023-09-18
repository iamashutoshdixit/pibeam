# Django imports
from django.contrib import admin, auth
from rest_framework.authtoken.models import TokenProxy
# User imports
from .models import User


class UserAdmin(auth.admin.UserAdmin):
    """
    Base model for authentication and user management
    """

    list_display = [
        "id",
        "username",
        "full_name",
        "role",
        "employee_id",
        "is_active",
    ]
    fieldsets = ()
    fields = (
        "username",
        "full_name",
        "role",
        "employee_id",
        "phone_no",
        "groups",
        "user_permissions",
        "is_active",
    )
    list_filter = [
        "is_active",
        "is_staff",
        "role",
    ]
    search_fields = ["username", "phone_no"]
    ordering = ('-id',)

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(User, UserAdmin)
admin.site.register(auth.models.Permission)
admin.site.unregister(TokenProxy)
