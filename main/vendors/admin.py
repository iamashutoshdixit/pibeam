# django imports
from django.contrib import admin

# project imports
from libs.mixins import BaseMixin

# app imports
from .models import Vendor


class VendorAdmin(BaseMixin):
    list_display = [
        "id",
        "name",
        "type",
        "address",
        "city",
        "state",
        "contact_person",
        "contact_number",
        "is_active",
    ]
    search_fields = ["name", "contact_person", "contact_number"]
    search_help_text = "Name, Contact Person, Contact Number"
    list_filter = ["city", "type", "is_active"]


admin.site.register(Vendor, VendorAdmin)
