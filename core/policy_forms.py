"""
Policy Forms

Forms for editing the TimeclockPolicy singleton via the portal UI.
"""

from django import forms
from .models import TimeclockPolicy


class TimeclockPolicyForm(forms.ModelForm):
    """
    Form for editing scheduling enforcement settings.

    Includes basic input constraints for grace period fields to avoid
    unreasonable values in the UI.
    """

    class Meta:
        model = TimeclockPolicy
        fields = (
            "strict_schedule_enforced",
            "allow_unscheduled_clock_in_when_not_strict",
            "grace_minutes_before_start",
            "grace_minutes_after_start",
        )
        widgets = {
            # Limit grace period range in the UI for better data quality
            "grace_minutes_before_start": forms.NumberInput(attrs={"min": 0, "max": 240}),
            "grace_minutes_after_start": forms.NumberInput(attrs={"min": 0, "max": 240}),
        }
