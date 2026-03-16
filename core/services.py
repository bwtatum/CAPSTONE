"""
Service Layer for TimeClock

All core business rules live here so views remain thin.

Responsibilities:
- Determine if an employee has an open shift
- Enforce schedule policy for clock in
- Apply grace window logic when configured
- Create WorkShift records using server side timestamps
- Manage meal breaks tied to a WorkShift
- Close WorkShift records and update status appropriately
"""

from datetime import datetime, timedelta
from django.utils import timezone

from .models import TimeclockPolicy, ScheduledShift, WorkShift, MealBreak


def get_open_shift(employee):
    """
    Returns the employee's current open shift or None.

    A shift is open when clock_out is null.
    """
    return WorkShift.objects.filter(employee=employee, clock_out__isnull=True).first()


def get_open_break(shift):
    """
    Returns the current open meal break for a shift or None.
    A break is open when end_time is null.
    """
    if shift is None:
        return None
    return shift.meal_breaks.filter(end_time__isnull=True).first()


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
        if scheduled is None:
            return False, "No scheduled shift today. Clock in not allowed."

        start_dt = timezone.make_aware(datetime.combine(today, scheduled.start_time))
        early_ok = start_dt - timedelta(minutes=policy.grace_minutes_before_start)
        late_ok = start_dt + timedelta(minutes=policy.grace_minutes_after_start)

        if policy.grace_minutes_before_start or policy.grace_minutes_after_start:
            if not (early_ok <= now <= late_ok):
                return False, "Clock in outside allowed time window."
    else:
        if scheduled is None and not policy.allow_unscheduled_clock_in_when_not_strict:
            return False, "Unscheduled clock in not allowed by policy."

    shift = WorkShift.objects.create(
        employee=employee,
        scheduled_shift=scheduled,
        clock_in=timezone.now(),
        status=WorkShift.Status.OPEN,
    )

    if scheduled is None:
        shift.status = WorkShift.Status.FLAGGED
        shift.save(update_fields=["status"])
        return True, "Clocked in. No schedule found so this shift was flagged as unscheduled."

    return True, "Clocked in successfully."


def start_meal_break(employee):
    """
    Starts a meal break for the employee's current open shift.

    Enforces:
    - Employee must have an open shift
    - Only one open break at a time per shift
    """
    shift = get_open_shift(employee)
    if shift is None:
        return False, "You must clock in before starting a meal break."

    if get_open_break(shift) is not None:
        return False, "Meal break already active."

    MealBreak.objects.create(
        shift=shift,
        start_time=timezone.now(),
    )

    return True, "Meal break started."


def end_meal_break(employee):
    """
    Ends the active meal break for the employee's current open shift.

    Enforces:
    - Employee must have an open shift
    - Must have an active break to end

    Rule:
    - If break is under 30 minutes, flag the shift for admin review
    """
    shift = get_open_shift(employee)
    if shift is None:
        return False, "No open shift."

    brk = get_open_break(shift)
    if brk is None:
        return False, "No active meal break."

    brk.end_time = timezone.now()
    brk.save(update_fields=["end_time"])

    duration_seconds = int((brk.end_time - brk.start_time).total_seconds())
    min_seconds = 30 * 60

    if duration_seconds < min_seconds:
        shift.status = WorkShift.Status.FLAGGED
        shift.save(update_fields=["status"])
        return True, "Meal break ended. Break was under 30 minutes so the shift was flagged."

    return True, "Meal break ended."


def clock_out(employee):
    """
    Clocks an employee out of their open shift.

    Enforces:
    - Must have an open shift to clock out from
    - Cannot clock out while a meal break is active

    Status handling:
    - OPEN shifts become CLOSED
    - FLAGGED or EDITED status is not overridden
    """
    shift = WorkShift.objects.filter(employee=employee, clock_out__isnull=True).first()
    if shift is None:
        return False, "No open shift to clock out from."

    if get_open_break(shift) is not None:
        return False, "End your meal break before clocking out."

    shift.clock_out = timezone.now()

    if shift.status == WorkShift.Status.OPEN:
        shift.status = WorkShift.Status.CLOSED

    shift.save(update_fields=["clock_out", "status"])
    return True, "Clocked out successfully."