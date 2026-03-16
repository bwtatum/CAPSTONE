"""
Core Data Models for TimeClock

This module defines the database schema for:
- TimeclockPolicy: singleton settings controlling scheduling and admin edit rules
- ScheduledShift: planned shift created by portal admins
- WorkShift: actual clock in and clock out records created by employees
- MealBreak: meal break records tied to a WorkShift
- ShiftEditLog: audit trail for administrative edits to WorkShift timestamps

High level design:
Views should remain thin and delegate business rules to the service layer.
"""

from datetime import timedelta

from django.conf import settings
from django.db import models


class TimeclockPolicy(models.Model):
    """
    Singleton policy record controlling global timeclock behavior.

    Intended usage:
    Use TimeclockPolicy.get_solo() anywhere policy values are needed.
    """

    strict_schedule_enforced = models.BooleanField(default=True)

    allow_unscheduled_clock_in_when_not_strict = models.BooleanField(default=True)
    grace_minutes_before_start = models.PositiveIntegerField(default=0)
    grace_minutes_after_start = models.PositiveIntegerField(default=0)

    allow_admin_time_edits = models.BooleanField(default=True)
    require_admin_edit_reason = models.BooleanField(default=True)

    @classmethod
    def get_solo(cls) -> "TimeclockPolicy":
        """
        Returns the singleton policy record.

        Creates pk=1 if it does not exist.
        """
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self) -> str:
        return "Timeclock policy"


class ScheduledShift(models.Model):
    """
    Planned shift for an employee on a given date.

    Admins can create or update these via the portal schedule page.
    Used for strict schedule enforcement and for associating actual shifts with plans.
    """

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_canceled = models.BooleanField(default=False)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "date"],
                name="uniq_employee_date_schedule",
            )
        ]

    def __str__(self) -> str:
        return f"{self.employee} {self.date} {self.start_time} to {self.end_time}"


class WorkShift(models.Model):
    """
    Actual worked shift produced by clock in and clock out actions.

    May optionally be linked to a ScheduledShift.
    A shift is considered open when clock_out is null.
    """

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        CLOSED = "CLOSED", "Closed"
        EDITED = "EDITED", "Edited"
        FLAGGED = "FLAGGED", "Flagged"

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    scheduled_shift = models.ForeignKey(
        ScheduledShift,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="edited_workshifts",
    )
    edit_reason = models.CharField(max_length=255, blank=True)

    def is_open(self) -> bool:
        return self.clock_out is None

    def total_seconds(self) -> int:
        """
        Total shift duration in seconds (clock_out - clock_in).
        Returns 0 if shift is still open.
        """
        if not self.clock_out:
            return 0
        return int((self.clock_out - self.clock_in).total_seconds())

    def break_seconds(self) -> int:
        """
        Total meal break seconds for this shift.
        Only counts breaks that have an end_time.
        """
        total = 0
        for b in self.meal_breaks.all():
            if b.end_time:
                total += int((b.end_time - b.start_time).total_seconds())
        return total

    def worked_seconds(self) -> int:
        """
        Payable worked seconds = total_seconds - break_seconds.
        """
        total = self.total_seconds()
        if total <= 0:
            return 0
        return max(0, total - self.break_seconds())

    def fmt_hhmm(self, seconds: int) -> str:
        """
        Format seconds as H:MM.
        """
        td = timedelta(seconds=int(seconds))
        total_minutes = int(td.total_seconds() // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours}:{minutes:02d}"

    def total_hhmm(self) -> str:
        return self.fmt_hhmm(self.total_seconds())

    def breaks_hhmm(self) -> str:
        return self.fmt_hhmm(self.break_seconds())

    def worked_hhmm(self) -> str:
        return self.fmt_hhmm(self.worked_seconds())

    def __str__(self) -> str:
        return f"{self.employee} {self.clock_in} to {self.clock_out or 'OPEN'}"


class MealBreak(models.Model):
    """
    Meal break tied to a WorkShift.

    A break is open when end_time is null.
    Only one open break should exist per shift.
    """

    shift = models.ForeignKey(
        WorkShift,
        on_delete=models.CASCADE,
        related_name="meal_breaks",
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_open(self) -> bool:
        return self.end_time is None

    def duration_seconds(self) -> int:
        if not self.end_time:
            return 0
        return int((self.end_time - self.start_time).total_seconds())

    def __str__(self) -> str:
        return f"Meal break {self.shift_id} {self.start_time} to {self.end_time or 'OPEN'}"


class ShiftEditLog(models.Model):
    """
    Audit log for WorkShift edits made by admins.

    Records:
    - who edited
    - when edited
    - why edited
    - what field changed and the old and new values
    """

    work_shift = models.ForeignKey(WorkShift, on_delete=models.CASCADE, related_name="edit_logs")
    edited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="shift_edits")
    edited_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255)

    field_name = models.CharField(max_length=50)
    old_value = models.CharField(max_length=100, blank=True)
    new_value = models.CharField(max_length=100, blank=True)

    def __str__(self) -> str:
        return f"{self.work_shift_id} {self.field_name} {self.edited_at}"