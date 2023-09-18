# python imports
import logging
from datetime import datetime
# django imports
from django.contrib import admin, messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, path
from django.utils.html import escape, mark_safe
from django.shortcuts import render
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
# project imports
from vendors.models import Vendor
from libs.mixins import BaseMixin, BaseLogMixin, ExportCSVMixin
from libs.helpers import S3FileUpload
# app imports
from .forms import (
    ChangeOnboardingStatus,
    ChangeDriverStatus,
    OnboardingDocumentUploadForm,
)
from .models import (
    Driver,
    Onboarding,
    DriverContract,
    DriverContractLog,
)

logger = logging.getLogger(__name__)


class OnboardingAdmin(BaseMixin):
    list_display = [
        "id",
        "full_name",
        "mobile_no",
        "aadhar_number",
        "house_no",
        "street",
        "locality",
        "city",
        "status",
        "updated_by",
        "aadhar_verified",
        "created_at",
    ]
    list_filter = [
        "city",
        "status",
    ]
    search_fields = ["full_name", "mobile_no"]
    search_help_text = "Full Name, Mobile No"
    actions = ["change_status", "upload_documents",]

    def photo_tag(self, obj=None):
        """
        return html tag to show photo of driver
        """
        return mark_safe(
            f'<div>\
                  <img style="margin-right: 1em;\
                       max-width: 30%" src="{obj.photo}"/>\
              </div>\
            '
        )

    def passbook_images(self, obj=None):
        """
        return html tag of passbook images
        """
        return mark_safe(
            f'<div>\
                  <img style="margin-right: 1em;\
                       max-width: 30%" src="{obj.passbook_front}"/>\
              </div>\
            '
        )
    
    def aadhar_images(self, obj=None):
        """
        return html tag of aadhar card
        """
        return mark_safe(
            f'<div>\
                  <img style="margin-right: 1em;\
                       max-width: 30%" src="{obj.aadhar_front}"/>\
                  <img style="max-width: 30%" src="{obj.aadhar_back}"/>\
              </div>\
            '
        )

    def pan_images(self, obj=None):
        """
        return pan images
        """
        if obj.pan_front is not None:
            return mark_safe(
                f'<div>\
                    <img style="margin-right: 1em; max-width: 30%" \
                        src="{obj.pan_front}"/>\
                </div>\
                '
            )
        return None

    def dl_images(self, obj=None):
        """
        return dl images
        """
        if (
            obj.driver_license_front is not None or
            obj.driver_license_back is not None
        ):
            return mark_safe(
                f'<div>\
                    <img style="margin-right: 1em; max-width: 30%"\
                        src="{obj.driver_license_front}"/>\
                    <img style="max-width: 30%"\
                        src="{obj.driver_license_back}"/>\
                </div>\
                '
            )
        return None

    photo_tag.short_description = "Photo"
    passbook_images.short_description = "Passbook Images"
    aadhar_images.short_description = "Aadhar Card Images"
    pan_images.short_description = "PAN Card Images"
    dl_images.short_description = "Driving License Images"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            self.readonly_fields = [
                "photo_tag",
                "aadhar_images",
                "passbook_images",
                "pan_images",
                "dl_images",
                "status",
                "is_active",
                "created_at",
                "updated_at",
                "updated_by",
                "remarks",
            ]
        return self.readonly_fields

    def change_status(self, request, queryset):
        """
        change status of onboarding
        """
        if "set_status" in request.POST:
            form = ChangeOnboardingStatus(request.POST)
            if form.is_valid():
                status = form.cleaned_data["status"]
                remarks = form.cleaned_data["remarks"]
                vendor = form.cleaned_data["vendor"]
                if len(queryset) > 1:
                    return HttpResponse(
                        "please select one candidate at a time"
                    )
                if status == "3" and not remarks:
                    return HttpResponse("remarks required if rejected")
                for obj in queryset:
                    if obj.status is Onboarding.Status.APPROVED.value:
                        return HttpResponse("driver has been approved already")
                    obj.status = int(status)
                    obj.remarks = remarks
                    try:
                        if vendor is not None:
                            vendor = Vendor.objects.get(pk=vendor.id)
                    except Vendor.DoesNotExist:
                        vendor = None
                        logger.info(
                            "{} INFO Vendor with pk {} does not exist.".format(
                                datetime.now(),
                                vendor,
                            )
                        )
                    obj.vendor = vendor
                    obj.updated_by = request.user
                    obj.save()
                    # update the LogEntry for history
                    message = f"status has been\
                        marked - {Onboarding.Status(int(status)).name} with\
                        the following remarks - {remarks} &\
                        vendor - {vendor}"
                    ctype = ContentType.objects.get_for_model(Onboarding)
                    LogEntry.objects.log_action(
                        user_id=request.user.id,
                        content_type_id=ctype.id,
                        object_id=obj.id,
                        object_repr=str(obj),
                        change_message=message,
                        action_flag=CHANGE,
                    )
                    messages.add_message(
                        request,
                        messages.INFO,
                        message,
                    )
                return HttpResponseRedirect(".")
        else:
            form = ChangeOnboardingStatus()

        return render(
            request,
            "drivers/html/change_status.html",
            {"title": "Choose status", "objects": queryset, "form": form},
        )

    def upload_documents(self, request, queryset):
        onboarding = queryset.first()
        if "set_status" in request.POST:
            form = OnboardingDocumentUploadForm(request.POST)
            if form.is_valid():
                passbook_front = request.FILES.get('passbook_front')
                image_upload = S3FileUpload()
                if passbook_front is not None:
                    success, passbook_front_url = image_upload.upload_file(
                        passbook_front, 
                        settings.AWS_CONFIG["S3"]["FOLDERS"]["driver-kyc-documents"],
                    )
                    if success is False:
                        return messages.add_message(
                            request,
                            messages.ERROR,
                            f"Error while uploading the passbook_front. Please try again.",
                        )
                    onboarding.passbook_front = passbook_front_url
                    onboarding.save()
                messages.add_message(
                    request,
                    messages.INFO,
                    f"Documents uploaded for driver {onboarding.mobile_no}.",
                )
                logger.info(
                    "Documents uploaded for driver {}".format(
                        onboarding.mobile_no,
                    )
                )
            return HttpResponseRedirect(".")
        else:
            if queryset.count() > 1:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"please select one vehicle at a time",
                )
                return HttpResponseRedirect(".")
            form = OnboardingDocumentUploadForm()

        return render(
            request,
            "services/html/servicing.html",
            {"title": "Onboarding Documents", "objects": queryset, "form": form, "action": "upload_documents"},
        )


    def has_add_permission(self, request, obj=None):
        return False



class DriverAdmin(BaseMixin, ExportCSVMixin):
    list_display = [
        "id",
        "get_full_name",
        "user_str",
        "onboarding_str",
        "get_mobile_no",
        "get_city",
        "get_has_driver_license",
        "doj",
        "app_version",
        "contract_accepted",
        "is_active",
    ]
    list_filter = [
        "is_active",
        "onboarding__has_driver_license",
        "contract_accepted",
        "onboarding__city",
        "app_version",
    ]
    search_fields = ["onboarding__full_name", "onboarding__mobile_no"]
    search_help_text = "Full Name, Mobile No"
    readonly_fields = [
        "full_name",
        "dob",
        "mobile_no",
        "house_no",
        "street",
        "locality",
        "city",
        "pincode",
        "own_house",
        "aadhar_number",
        "pan_number",
        "account_number",
        "account_name",
        "ifsc_code",
        "doj",
        "dol",
        "photo_tag", 
        "aadhar_images", 
        "pan_images", 
        "dl_images", 
        "app_version", 
        "contract_accepted", 
        "contract",
        "vendor",
        "remarks",
        "updated_by",
        "created_at",
        "updated_at",
        "is_active",
    ]
    actions = ["change_status", "export_selected"]
    csv_fields = [
            "onboarding.full_name",
            "onboarding.dob",
            "onboarding.mobile_no",
            "onboarding.house_no",
            "onboarding.street",
            "onboarding.locality",
            "onboarding.city",
            "onboarding.pincode",
            "onboarding.own_house",
            "onboarding.aadhar_number",
            "onboarding.pan_number",
            "onboarding.account_number",
            "onboarding.account_name",
            "onboarding.ifsc_code",
            "onboarding.photo",
            "onboarding.aadhar_front",
            "onboarding.aadhar_back",
            "onboarding.pan_front",
            "onboarding.driver_license_front",
            "onboarding.driver_license_back",
            "doj",
            "dol",
            "vendor.id",
            "app_version",
            "contract_accepted",
            "is_active",
        ]
    model = Driver

    def user_str(self, obj):
        if obj.user is not None:
            link = reverse("admin:users_user_change", args=[obj.user.id])
            return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.user.__str__())}</a>')
        return None
    user_str.short_description = 'User'

    def onboarding_str(self, obj):
        if obj.onboarding is not None:
            link = reverse("admin:drivers_onboarding_change", args=[obj.onboarding.id])
            return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.onboarding.__str__())}</a>')
        return None
    onboarding_str.short_description = 'Onboarding'

    def photo_tag(self, obj=None):
        return mark_safe(
            f'<div>\
                  <img style="margin-right: 1em; max-width: 30%"\
                       src="{obj.onboarding.photo}"/>\
              </div>\
            '
        )

    def aadhar_images(self, obj=None):
        return mark_safe(
            f'<div>\
                  <img style="margin-right: 1em; max-width: 30%"\
                       src="{obj.onboarding.aadhar_front}"/>\
                  <img style="max-width: 30%" src="{obj.onboarding.aadhar_back}"/>\
              </div>\
            '
        )

    def pan_images(self, obj=None):
        """
        return pan images
        """
        if obj.onboarding.pan_front is not None:
            return mark_safe(
                f'<div>\
                    <img style="margin-right: 1em; max-width: 30%" \
                        src="{obj.onboarding.pan_front}"/>\
                </div>\
                '
            )
        return None

    def dl_images(self, obj=None):
        if (
            obj.onboarding.driver_license_front is not None or
            obj.onboarding.driver_license_back is not None
        ):
            return mark_safe(
                f'<div>\
                    <img style="margin-right: 1em; max-width: 30%"\
                        src="{obj.onboarding.driver_license_front}"/>\
                    <img style="max-width: 30%"\
                        src="{obj.onboarding.driver_license_back}"/>\
                </div>\
                '
            )
        return None

    def get_full_name(self, obj):
        return obj.onboarding.full_name

    def get_mobile_no(self, obj):
        return obj.onboarding.mobile_no

    def get_city(self, obj):
        return obj.onboarding.city
        
    def get_has_driver_license(self, obj):
        return obj.onboarding.has_driver_license
    
    get_full_name.short_description = "Full Name"
    get_mobile_no.short_description = "Mobile No"
    get_city.short_description = "City"
    get_has_driver_license.short_description = "Has Driving License"
    photo_tag.short_description = "Photo"
    aadhar_images.short_description = "Aadhar Card Images"
    pan_images.short_description = "PAN Card Images"
    dl_images.short_description = "Driving License Images"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "export-driver-csv/",
                self.export_selected,
                name="export_driver_csv",
            ),
        ]
        return my_urls + urls

    def has_add_permission(self, request):
        return False

    def change_status(self, request, queryset):
        """
        change status of driver
        """
        if "set_status" in request.POST:
            form = ChangeDriverStatus(request.POST)
            if form.is_valid():
                status = form.cleaned_data["status"]
                remarks = form.cleaned_data["remarks"]
                dol = form.cleaned_data["date_of_leaving"]
                obj = queryset.first()
                if bool(int(status)) is obj.is_active:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        f"driver is already in the marked state.",
                    )
                    return HttpResponseRedirect(".")
                if status == "0":
                    if not dol:
                        messages.add_message(
                            request,
                            messages.ERROR,
                            "Date of Leaving is mandatory for Attritions.",
                        )
                        return HttpResponseRedirect(".")
                    obj.dol = dol
                if status == "1":
                    obj.dol = None
                obj.is_active = bool(int(status))
                obj.remarks = remarks
                obj.updated_by = request.user
                obj.save()

                # update the LogEntry for history
                message = f"is_active has been \
                    marked - {obj.is_active} with the following\
                    remarks - {remarks}"
                ctype = ContentType.objects.get_for_model(Driver)
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ctype.id,
                    object_id=obj.id,
                    object_repr=str(obj),
                    change_message=message,
                    action_flag=CHANGE,
                )
                return HttpResponseRedirect(".")
        else:
            if queryset.count() > 1:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"Please select one driver at a time.",
                )
                return HttpResponseRedirect(".")
            form = ChangeDriverStatus()

        return render(
            request,
            "drivers/html/change_status.html",
            {"title": "Choose status", "objects": queryset, "form": form},
        )


class DriverContractAdmin(BaseMixin):
    list_display = [
        "name",
        "description",
        "url",
    ]
    readonly_fields = ["created_at", "updated_at"]


class DriverContractLogAdmin(BaseLogMixin):
    list_display = [
        "contract",
        "driver",
        "created_at",
    ]


admin.site.register(Onboarding, OnboardingAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(DriverContract, DriverContractAdmin)
admin.site.register(DriverContractLog, DriverContractLogAdmin)
