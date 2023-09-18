import logging
# django imports
from django.contrib import admin, messages
from django.shortcuts import render
from django.urls import reverse, path
from django.utils.html import escape, mark_safe
from django.http import HttpResponseRedirect
from django.forms.models import model_to_dict
from django.urls import path
from django.conf import settings
# project imports
from libs.mixins import BaseMixin, BaseLogMixin, ExportCSVMixin
from libs.helpers import S3FileUpload
# app imports
from .models import Client, ClientContractLog, ClientStore, Pricing
from .forms import ClientDocumentUploadForm, PricingForm

logger = logging.getLogger(__name__)


class ClientAdmin(BaseMixin, ExportCSVMixin):
    list_display = [
        "id",
        "name",
        "gst",
        "address",
        "city",
        "state",
        "contact_person",
        "contact_number",
        "is_active",
    ]
    model = Client
    search_fields = ["name", "contact_person"]
    search_help_text = "Name, Contact Person"
    list_filter = ["city", "is_active"]
    actions = ["upload_documents", "export_selected"]
    readonly_fields = ["updated_by", "contract"]
    csv_fields = model.get_fields()

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "export-client-csv/",
                self.export_selected,
                name="export_client_csv",
            ),
        ]
        return my_urls + urls

    def upload_documents(self, request, queryset):
        client = queryset.first()
        if "set_status" in request.POST:
            form = ClientDocumentUploadForm(request.POST, request.FILES)
            if form.is_valid():
                contract_document = request.FILES.get('contract_document')
                image_upload = S3FileUpload()
                success, contract_document_url = image_upload.upload_file(
                    contract_document, 
                    settings.AWS_CONFIG["S3"]["FOLDERS"]["client-documents"],
                )
                if success is False:
                    return messages.add_message(
                        request,
                        messages.ERROR,
                        f"Error while uploading the contract document. Please try again.",
                    )
                client.contract = contract_document_url
                client.updated_by = request.user
                client.save()
                messages.add_message(
                    request,
                    messages.INFO,
                    f"Documents uploaded for client {client.name}.",
                )
                logger.info(
                    "Documents uploaded for client {}".format(
                        client.name,
                    )
                )
            return HttpResponseRedirect(".")
        else:
            if queryset.count() > 1:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"please select one client at a time",
                )
                return HttpResponseRedirect(".")
            form = ClientDocumentUploadForm()

        return render(
            request,
            "form_with_fileupload.html",
            {"title": "Client Documents", "objects": queryset, "form": form, "action": "upload_documents"},
        )

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        if change is True:
            new = model_to_dict(obj)
            old = form.initial
            changed = ["{0}: {1} -> {2}".format(key, old[key], new[key]) for key in old if old[key] != new[key]]
            message = "Fields Changed " + ", ".join(changed)
            self.log_change(request, obj, message=message)
        super().save_model(request, obj, form, change)

    def log_change(self, request, object, message):
        """
        Override the default log entry for changes
        """
        if isinstance(message, str) and message.startswith("Fields"):
            super().log_change(request, object, message)
        return False


class ClientStoreAdmin(BaseMixin, ExportCSVMixin):
    list_display = [
        "id",
        "client_str",
        "name",
        "address",
        "city",
        "state",
        "contact_number",
        "is_active",
    ]
    model = ClientStore
    search_fields = ["name", "client__name", "contact_number"]
    search_help_text = "Name, Client Name, Contact Number"
    list_filter = ["city", "is_active"]
    actions = ["export_selected"]
    csv_fields = model.get_fields()

    def client_str(self, obj):
        if obj.client is not None:
            link = reverse("admin:clients_client_change", args=[obj.client.id])
            return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.client.__str__())}</a>')
        return None
    client_str.short_description = 'Client'

    def get_google_maps_loc(self, obj):
        return mark_safe(
            f'<div>\
                  <a target="_blank" href="http://maps.google.com/maps?q={obj.latitude},{obj.longitude}"> link</a>\
              </div>\
            '
        )
    get_google_maps_loc.short_description = "Location"


    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "export-clientstore-csv/",
                self.export_selected,
                name="export_clientstore_csv",
            ),
        ]
        return my_urls + urls

class ClientContractLogAdmin(BaseLogMixin):
    list_display = [
        "id",
        "client",
        "old_contract",
        "new_contract",
        "created_by",
        "created_at",
    ]
    model = ClientContractLog
    search_fields = ["client__name"]
    search_help_text = "Client Name"
    date_hierarchy = 'created_at'
    actions = ["export_selected"]
    csv_fields = model.get_fields()


class PricingAdmin(BaseMixin, ExportCSVMixin):
    list_display = [
        "id",
        "title",
        "client_str",
        "model",
        "type",
        "price",
    ]
    form = PricingForm
    model = Pricing
    search_fields = ["client__name"]
    search_help_text = "Client Name"
    date_hierarchy = 'created_at'
    actions = ["export_selected"]
    csv_fields = model.get_fields()

    def client_str(self, obj):
        if obj.client is not None:
            link = reverse("admin:clients_client_change", args=[obj.client.id])
            return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.client.__str__())}</a>')
        return None
    client_str.short_description = 'Client'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is not None:
            form.pid = obj.id
        form.base_fields["client"].queryset = Client.objects.filter(is_active=True)
        try:
            # remove add / edit / remove actions for drivers
            field = form.base_fields["client"]
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
            field = form.base_fields["client_store"]
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
        except KeyError:
            pass
        return form


admin.site.register(Client, ClientAdmin)
admin.site.register(ClientStore, ClientStoreAdmin)
admin.site.register(ClientContractLog, ClientContractLogAdmin)
admin.site.register(Pricing, PricingAdmin)
