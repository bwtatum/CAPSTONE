"""
Scheduling Forms

Forms for creating and updating ScheduledShift records via the admin portal UI.
"""

from django import forms
from django.contrib.auth import get_user_model

from .models import ScheduledShift

User = get_user_model()


class ScheduledShiftForm(forms.ModelForm):
    """
    Form used by portal schedule management.

    Allows admins to create or update one scheduled shift per employee per day.
    """

    employee = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username")
    )

    class Meta:
        model = ScheduledShift
        fields = ["employee", "date", "start_time", "end_time", "is_canceled", "notes"]
        widgets = {
            # Use native browser date and time pickers
            "date": forms.DateInput(attrs={"type": "date"}),
            # step 900 seconds equals 15 minute increments
            "start_time": forms.TimeInput(attrs={"type": "time", "step": "900"}),
            "end_time": forms.TimeInput(attrs={"type": "time", "step": "900"}),
            "notes": forms.TextInput(attrs={"placeholder": "Optional notes"}),
        }
