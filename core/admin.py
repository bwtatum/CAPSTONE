"""
Django Admin Configuration

Registers TimeClock models in the Django admin site and adds admin specific behavior.

Key behaviors:
- TimeclockPolicy is treated as a singleton and redirects the changelist to the single record.
- WorkShift admin edits are validated via WorkShiftAdminForm.
- WorkShift time edits are audited via ShiftEditLog for transparency and payroll traceability.
"""

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .forms import WorkShiftAdminForm
from .models import TimeclockPolicy, ScheduledShift, WorkShift, ShiftEditLog


@admin.register(TimeclockPolicy)
class TimeclockPolicyAdmin(admin.ModelAdmin):
    """
    Admin UI for the global timeclock policy.

    This model is intended to exist as a single record.
    The admin UI enforces that behavior by:
    - Preventing additional records from being created
    - Redirecting the changelist page to the singleton change page
    """

    fieldsets = (
        (
            "Schedule enforcement",
            {
                "fields": (
                    "strict_schedule_enforced",
                    "allow_unscheduled_clock_in_when_not_strict",
                    "grace_minutes_before_start",
                    "grace_minutes_after_start",
                )
            },
        ),
        (
            "Admin controls",
            {
                "fields": (
                    "allow_admin_time_edits",
                    "require_admin_edit_reason",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        """
        Prevents creation of multiple policy objects.

        The policy should be edited, not created repeatedly.
        """
        return not TimeclockPolicy.objects.exists()

    def changelist_view(self, request, extra_context=None):
        """
        Redirects the policy changelist to the singleton edit page.

        This makes the admin UI behave like a settings page.
        """
        obj, _ = TimeclockPolicy.objects.get_or_create(pk=1)
        url = reverse("admin:core_timeclockpolicy_change", args=(obj.pk,))
        return redirect(url)


@admin.register(ScheduledShift)
class ScheduledShiftAdmin(admin.ModelAdmin):
    """
    Admin UI for scheduled shifts.

    Used by admins to create schedules which may be enforced by policy.
    """

    list_display = ("employee", "date", "start_time", "end_time", "is_canceled")
    list_filter = ("date", "is_canceled", "employee")
    search_fields = ("employee__username",)
    ordering = ("-date", "employee__username")


@admin.register(WorkShift)
class WorkShiftAdmin(admin.ModelAdmin):
    """
    Admin UI for actual worked shifts.

    Important behaviors:
    - Uses WorkShiftAdminForm to validate time changes and enforce edit reason rules.
    - If an admin changes clock in or clock out, the shift is marked as EDITED.
    - All changes are written to ShiftEditLog as an audit trail.
    """

    class Media:
        """
        Loads custom JavaScript in the admin page.

        This is typically used to enhance time selection UI.
        """
        js = ("core/admin_timepicker.js",)

    form = WorkShiftAdminForm
    list_display = ("employee", "clock_in", "clock_out", "status")
    list_filter = ("status", "employee")
    search_fields = ("employee__username",)
    ordering = ("-clock_in",)

    fields = (
        "employee",
        "scheduled_shift",
        "clock_in",
        "clock_out",
        "status",
        "edit_reason",
        "edited_by",
    )
    readonly_fields = ("edited_by",)

    def save_model(self, request, obj, form, change):
        """
        Saves WorkShift changes and records audit logs when times change.

        Audit logging is limited to fields that materially affect payroll accuracy:
        - clock_in
        - clock_out
        """

        changed_fields = []

        if change:
            # Load the previous state to compare changes
            old = WorkShift.objects.get(pk=obj.pk)

            if old.clock_in != obj.clock_in:
                changed_fields.append(("clock_in", str(old.clock_in), str(obj.clock_in)))
            if old.clock_out != obj.clock_out:
                changed_fields.append(("clock_out", str(old.clock_out), str(obj.clock_out)))

            if changed_fields:
                # Mark shift as edited and track who did it
                obj.status = WorkShift.Status.EDITED
                obj.edited_by = request.user
                obj.edit_reason = (obj.edit_reason or "").strip()

        super().save_model(request, obj, form, change)

        # Create a separate audit log entry for each changed field
        for field_name, old_val, new_val in changed_fields:
            ShiftEditLog.objects.create(
                work_shift=obj,
                edited_by=request.user,
                reason=obj.edit_reason or "Admin edit",
                field_name=field_name,
                old_value=old_val,
                new_value=new_val,
            )


@admin.register(ShiftEditLog)
class ShiftEditLogAdmin(admin.ModelAdmin):
    """
    Read only admin UI for shift edit audit logs.

    This supports accountability and simplifies investigating payroll disputes.
    """

    list_display = ("work_shift", "edited_by", "field_name", "edited_at")
    list_filter = ("field_name", "edited_by", "edited_at")
    search_fields = ("work_shift__employee__username", "edited_by__username", "reason")
    ordering = ("-edited_at",)
    readonly_fields = (
        "work_shift",
        "edited_by",
        "edited_at",
        "reason",
        "field_name",
        "old_value",
        "new_value",
    )
