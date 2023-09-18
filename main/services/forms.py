from django import forms
from dal import autocomplete
from crispy_forms.helper import FormHelper
# project imports
from config.models import Config
# app imports
from .models import Service


class ServiceForm(forms.ModelForm):
    issue_subtype = forms.ChoiceField(choices=[(v, v) for k,v in enumerate(Config.get_value("servicing_subtype"))])
    photos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = Service
        fields = "__all__"
        widgets = {
            'is_active': forms.HiddenInput(),
            'reportee': autocomplete.ModelSelect2(url='users-autocomplete', attrs={'data-minimum-input-length': 3}),
        }
        exclude = ('remarks', 'created_by', 'photos',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].widget.attrs['readonly'] = True
        self.fields['status'].widget.attrs['readonly'] = True
        self.helper = FormHelper()
        self.helper.form_id = 'id-my-form'
        self.helper.form_class = 'my-form'
