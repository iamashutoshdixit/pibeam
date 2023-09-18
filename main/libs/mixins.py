import datetime
from django.contrib import admin

# user imports
from libs.helpers import csv_dispatcher


class ExportCSVMixin():
    model = ""
    csv_fields = list()

    def get_repr(self, value): 
        if value is None:
            return "-"
        if isinstance(value, list):
            value = ", ".join(value)
        if isinstance(value, str) and "," in value:
            value = value.replace(",", "|")
        if isinstance(value, (datetime.date, datetime.time, int, float)):
            return str(value)
        if callable(value):
            return '%s' % value()
        return value

    def get_field(self, instance, field):
        field_path = field.split('.')
        attr = instance
        for elem in field_path:
            try:
                attr = getattr(attr, elem)
            except AttributeError:
                return None
        return attr

    def export_selected(self, request, queryset=None):
        fields = self.csv_fields
        csv = ""
        csv += ",".join(self.csv_fields) + "\n"
        if queryset is None:
            queryset = self.model.objects.all()
        for obj in queryset:
            row = [self.get_repr(self.get_field(obj, field)) for field in fields]
            csv += ",".join(row) + "\n"
        return csv_dispatcher(csv)


class BaseMixin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at',)
    show_full_result_count = False

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        # Exclude only for autocomplete
        if '/autocomplete/' in request.path:
            queryset = queryset.exclude(is_active=False)
        return queryset, use_distinct

    def has_delete_permission(self, request, obj=None):
        return False


class BaseLogMixin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
    show_full_result_count = False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False