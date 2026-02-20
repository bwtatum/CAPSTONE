"""
Admin Forms

Contains Django ModelForms used by the Django admin site.

Primary purpose:
- Validate WorkShift changes when an admin edits a shift in the admin UI
- Enforce policy requirements such as preventing time edits or requiring reasons
"""

from django import forms
from django.core.exceptions import ValidationError

from .models import TimeclockPolicy, WorkShift


class WorkShiftAdminForm(forms.ModelForm):
    """
    Form used by WorkShiftAdmin in admin.py.

    Validates:
    - clock_out must be after clock_in
    - admin time edits may be disabled by policy
    - admin edit reasons may be required by policy when times change
    """

    class Meta:
        model = WorkShift
        fields = "__all__"

    def clean(self):
        """
        Validates edits made in Django admin.

        This is intentionally strict because admin edits affect payroll accuracy.
        """
        cleaned = super().clean()

        clock_in = cleaned.get("clock_in")
        clock_out = cleaned.get("clock_out")

        # Basic chronological validation
        if clock_in and clock_out and clock_out <= clock_in:
            raise ValidationError("Clock out must be after clock in.")

        # If this is an existing object, check whether time values changed
        if self.instance and self.instance.pk:
            old = WorkShift.objects.get(pk=self.instance.pk)
            times_changed = (old.clock_in != clock_in) or (old.clock_out != clock_out)

            if times_changed:
                policy = TimeclockPolicy.get_solo()

                # Policy may disallow admin time edits entirely
                if not policy.allow_admin_time_edits:
                    raise ValidationError("Admin time edits are disabled by policy.")

                # Policy may require an explicit reason when changing times
                reason = (cleaned.get("edit_reason") or "").strip()
                if policy.require_admin_edit_reason and not reason:
                    raise ValidationError("Edit reason is required when changing times.")

        return cleaned
