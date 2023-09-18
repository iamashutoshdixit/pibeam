# Django imports
from django import forms
from crispy_forms.helper import FormHelper
from dal import autocomplete
from vendors.models import Vendor
# User imports
from .models import (
    Station, 
    Vehicle, 
    Battery, 
    Charger, 
    GPSTracker,
)


class BatteryForm(forms.ModelForm):
    is_active = forms.BooleanField(initial=True)
    model = forms.ChoiceField(choices=Battery.get_values("model"))
    protocol = forms.ChoiceField(choices=Battery.get_values("protocol"))
    chemistry = forms.ChoiceField(choices=Battery.get_values("chemistry"))

    class Meta:
        model = Battery
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.filter(is_active=True)
        self.fields['vendor'].queryset = Vendor.objects.filter(type=Vendor.TYPE.BATTERY.value, is_active=True)
        self.helper = FormHelper()
        self.helper.form_id = 'id-my-form'
        self.helper.form_class = 'my-form'


class ChargerForm(forms.ModelForm):
    is_active = forms.BooleanField(initial=True)
    type = forms.ChoiceField(choices=Charger.get_values("type"))
    connector = forms.ChoiceField(choices=Charger.get_values("connector"))
    wattage = forms.ChoiceField(choices=Charger.get_values("wattage"))

    class Meta:
        model = Charger
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.filter(is_active=True)
        self.fields['vendor'].queryset = Vendor.objects.filter(type=Vendor.TYPE.BATTERY.value, is_active=True)
        self.helper = FormHelper()
        self.helper.form_id = 'id-my-form'
        self.helper.form_class = 'my-form'


class GPSTrackerForm(forms.ModelForm):
    is_active = forms.BooleanField(initial=True)
    type = forms.ChoiceField(choices=GPSTracker.get_values("type"))

    class Meta:
        model = Battery
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.filter(is_active=True)
        self.fields['vendor'].queryset = Vendor.objects.filter(type=Vendor.TYPE.GPS_TRACKER.value, is_active=True)
        self.helper = FormHelper()
        self.helper.form_id = 'id-my-form'
        self.helper.form_class = 'my-form'


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(VehicleForm, self).__init__(*args, **kwargs)
        self.fields['dealer'].queryset = Vendor.objects.filter(type=Vendor.TYPE.VEHICLE, is_active=True)
        self.fields['financier'].queryset = Vendor.objects.filter(type=Vendor.TYPE.FINANCE, is_active=True)
        self.fields['station'].queryset = Station.objects.filter(is_active=True)
        self.helper = FormHelper()
        self.helper.form_id = 'id-my-form'
        self.helper.form_class = 'my-form'


class VehicleDocumentUploadForm(forms.Form):
    rc_document = forms.FileField(required=False)
    insurance_document = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-my-form'
        self.helper.form_class = 'my-form'
