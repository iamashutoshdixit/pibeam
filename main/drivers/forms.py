# django imports
from django import forms
from crispy_forms.helper import FormHelper

# app imports
from vendors.models import Vendor
from .models import (
    Onboarding,
    Driver,
)


class ChangeOnboardingStatus(forms.Form):
    status = forms.ChoiceField(choices=Onboarding.Status.choices)
    remarks = forms.CharField(max_length=250, required=False)
    vendor = forms.ModelChoiceField(
        required=False, 
        widget=forms.Select, 
        queryset=Vendor.objects.filter(type=Vendor.TYPE.DRIVER.value, is_active=True))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-my-form'
        self.helper.form_class = 'my-form'


class ChangeDriverStatus(forms.Form):
    status = forms.ChoiceField(choices=Driver.Status.choices)
    remarks = forms.CharField(max_length=250, required=True)
    date_of_leaving = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-my-form'
        self.helper.form_class = 'my-form'


class OnboardingDocumentUploadForm(forms.Form):
    passbook_front = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-my-form'
        self.helper.form_class = 'my-form'
