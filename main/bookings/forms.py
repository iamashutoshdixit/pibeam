# django imports
from django import forms
# app imports
from .models import Roster


class ChangeRosterStatus(forms.Form):
    statuses = Roster.STATUS.choices
    remove_statuses = [(3, 'Service'), ]
    statuses = list(set(statuses) - set(remove_statuses))
    status = forms.ChoiceField(choices=statuses)
    remarks = forms.CharField(max_length=250, required=False)


class ChangeTripStatus(forms.Form):
    status = forms.ChoiceField(choices=Roster.STATUS.choices)
