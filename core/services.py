"""
Service Layer for TimeClock

All core business rules live here so views remain thin.

Responsibilities:
- Determine if an employee has an open shift
- Enforce schedule policy for clock in
- Apply grace window logic when configured
- Create WorkShift records using server side timestamps
- Close WorkShift records and update status appropriately
"""

from datetime import datetime
from django.utils import timezone

from .models import TimeclockPolicy, ScheduledShift, WorkShift


def get_open_shift(employee):
    """
    Returns the employee's current open shift or None.

    A shift is open when clock_out is null.
    """
    return WorkShift.objects.filter(employee=employee, clock_out__isnull=True).first()


def clock_in(employee):
    """
    Clocks an employee in and creates a WorkShift.

    Enforces:
    - One open shift at a time
    - Strict schedule rules when enabled
    - Grace window rules when configured
    - Optional unscheduled clock in allowance when not strict

    Returns:
        tuple[bool, str]: success flag and user friendly message
    """
    policy = TimeclockPolicy.get_solo()

    # Prevent double clock in while already on shift
    if WorkShift.objects.filter(employee=employee, clock_out__isnull=True).exists():
        return False, "You already have an open shift."

    today = timezone.localdate()
    now = timezone.localtime()

    scheduled = ScheduledShift.objects.filter(
        employee=employee,
        date=today,
        is_canceled=False,
    ).first()

    if policy.strict_schedule_enforced:
        # In strict mode, a schedule is required
        if scheduled is None:
            return False, "No scheduled shift today. Clock in not allowed."

        # Grace window enforcement is optional and based on configured minutes
        start_dt = timezone.make_aware(datetime.combine(today, scheduled.start_time))
        early_ok = start_dt - timezone.timedelta(minutes=policy.grace_minutes_before_start)
        late_ok = start_dt + timezone.timedelta(minutes=policy.grace_minutes_after_start)

        if policy.grace_minutes_before_start or policy.grace_minutes_after_start:
            if not (early_ok <= now <= late_ok):
                return False, "Clock in outside allowed time window."
    else:
        # Non strict mode can still block unscheduled clock in based on policy
        if scheduled is None and not policy.allow_unscheduled_clock_in_when_not_strict:
            return False, "Unscheduled clock in not allowed by policy."

    # Always record server side timestamps for auditability
    shift = WorkShift.objects.create(
        employee=employee,
        scheduled_shift=scheduled,
        clock_in=timezone.now(),
        status=WorkShift.Status.OPEN,
    )

    # If no schedule exists, flag the shift for admin review
    if scheduled is None:
        shift.status = WorkShift.Status.FLAGGED
        shift.save(update_fields=["status"])
        return True, "Clocked in. No schedule found so this shift was flagged as unscheduled."

    return True, "Clocked in successfully."


def clock_out(employee):
    """
    Clocks an employee out of their open shift.

    Enforces:
    - Must have an open shift to clock out

    Status handling:
    - OPEN shifts become CLOSED
    - FLAGGED or EDITED status is not overridden
    """
    shift = WorkShift.objects.filter(employee=employee, clock_out__isnull=True).first()
    if shift is None:
        return False, "No open shift to clock out from."

    shift.clock_out = timezone.now()

    # Do not override flagged or edited shifts
    if shift.status == WorkShift.Status.OPEN:
        shift.status = WorkShift.Status.CLOSED

    shift.save(update_fields=["clock_out", "status"])
    return True, "Clocked out successfully."
