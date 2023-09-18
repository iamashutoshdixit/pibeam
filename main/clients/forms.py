# Django imports
from django import forms
from crispy_forms.helper import FormHelper
from django.core.exceptions import ValidationError
# app imports
from .models import Pricing


class ClientDocumentUploadForm(forms.Form):
    contract_document = forms.FileField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-my-form'
        self.helper.form_class = 'my-form'


class PricingForm(forms.ModelForm):

    class Meta:
        model = Pricing
        fields = '__all__'

    def clean(self):
        pricings = Pricing.objects.filter(
            client=self.cleaned_data['client'],
            type=self.cleaned_data['type'],
            model=self.cleaned_data['model'],
        )
        if hasattr(self, "pid") and self.pid is not None:
            pricings = pricings.exclude(id=self.pid)
        if pricings.count() > 0:
            if self.cleaned_data['client_store'] is not None:
                pricings = pricings.filter(
                    client_store__in=self.cleaned_data['client_store'],
                ).distinct()
                if pricings.count() > 0:
                    raise ValidationError("Pricing for the selection already exists")
            else:
                raise ValidationError("Pricing for the selection already exists")
        return self.cleaned_data