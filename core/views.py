"""
Core Views for TimeClock

Views are intentionally thin and delegate business rules to services.py.

This keeps:
- request handling in views
- business logic in services
- persistence rules in models
"""

from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.utils import timezone

from . import services
from .models import WorkShift, ScheduledShift, TimeclockPolicy
from .permissions import portal_admin_required
from .policy_forms import TimeclockPolicyForm
from .schedule_forms import ScheduledShiftForm


def landing(request):
    return render(request, "core/landing.html")


@login_required
@portal_admin_required
def portal_home(request):
    return render(request, "core/portal_home.html")


@login_required
@portal_admin_required
def admin_schedule(request):
    policy = TimeclockPolicy.get_solo()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "save_policy":
            policy_form = TimeclockPolicyForm(request.POST, instance=policy)
            schedule_form = ScheduledShiftForm()

            if policy_form.is_valid():
                policy_form.save()
                messages.success(request, "Policy updated.")
                return redirect("admin_schedule")
            messages.error(request, "Please fix the policy form errors.")
        else:
            schedule_form = ScheduledShiftForm(request.POST)
            policy_form = TimeclockPolicyForm(instance=policy)

            if schedule_form.is_valid():
                data = schedule_form.cleaned_data

                ScheduledShift.objects.update_or_create(
                    employee=data["employee"],
                    date=data["date"],
                    defaults={
                        "start_time": data["start_time"],
                        "end_time": data["end_time"],
                        "is_canceled": data["is_canceled"],
                        "notes": data["notes"],
                    },
                )

                messages.success(request, "Schedule saved.")
                return redirect("admin_schedule")

            messages.error(request, "Please fix the schedule form errors.")
    else:
        schedule_form = ScheduledShiftForm()
        policy_form = TimeclockPolicyForm(instance=policy)

    today = timezone.localdate()
    upcoming = ScheduledShift.objects.filter(date__gte=today).order_by("date", "employee")[:50]

    return render(
        request,
        "core/admin_schedule.html",
        {
            "schedule_form": schedule_form,
            "policy_form": policy_form,
            "upcoming": upcoming,
        },
    )


@login_required
def timesheet(request):
    shifts = (
        WorkShift.objects
        .filter(employee=request.user)
        .prefetch_related("meal_breaks")
        .order_by("-clock_in")[:14]
    )
    return render(request, "core/timesheet.html", {"shifts": shifts})


@login_required
def home(request):
    current_shift = services.get_open_shift(request.user)

    break_active = False
    break_start_iso = ""

    if current_shift:
        open_break = services.get_open_break(current_shift)
        if open_break:
            break_active = True
            break_start_iso = timezone.localtime(open_break.start_time).isoformat()

    return render(
        request,
        "core/home.html",
        {
            "current_shift": current_shift,
            "break_active": break_active,
            "break_start_iso": break_start_iso,
        },
    )


@login_required
def clock_in(request):
    if request.method != "POST":
        return redirect("home")

    ok, msg = services.clock_in(request.user)
    if ok:
        messages.success(request, msg)
    else:
        messages.error(request, msg)
    return redirect("home")


@login_required
def clock_out(request):
    if request.method != "POST":
        return redirect("home")

    ok, msg = services.clock_out(request.user)
    if ok:
        messages.success(request, msg)
    else:
        messages.error(request, msg)
    return redirect("home")


@login_required
def meal_break_toggle(request):
    if request.method != "POST":
        return redirect("home")

    current_shift = services.get_open_shift(request.user)
    if not current_shift:
        messages.error(request, "Clock in first.")
        return redirect("home")

    open_break = services.get_open_break(current_shift)

    if open_break:
        ok, msg = services.end_meal_break(request.user)
    else:
        ok, msg = services.start_meal_break(request.user)

    if ok:
        messages.success(request, msg)
    else:
        messages.error(request, msg)

    return redirect("home")


@login_required
@portal_admin_required
def admin_timesheets(request):
    """
    Admin view of employee shifts.

    Filters via GET:
    - employee_id: user id
    - start: YYYY-MM-DD
    - end: YYYY-MM-DD
    """
    User = get_user_model()

    employees = User.objects.order_by("username")

    employee_id = request.GET.get("employee_id", "").strip()
    start_str = request.GET.get("start", "").strip()
    end_str = request.GET.get("end", "").strip()

    qs = WorkShift.objects.select_related("employee").prefetch_related("meal_breaks").order_by("-clock_in")

    if employee_id:
        qs = qs.filter(employee_id=employee_id)

    def parse_date(s):
        try:
            return date.fromisoformat(s)
        except Exception:
            return None

    start_date = parse_date(start_str) if start_str else None
    end_date = parse_date(end_str) if end_str else None

    if start_str and not start_date:
        messages.error(request, "Invalid start date format. Use YYYY-MM-DD.")
    if end_str and not end_date:
        messages.error(request, "Invalid end date format. Use YYYY-MM-DD.")

    if start_date:
        qs = qs.filter(clock_in__date__gte=start_date)
    if end_date:
        qs = qs.filter(clock_in__date__lte=end_date)

    shifts = qs[:200]

    return render(
        request,
        "core/admin_timesheets.html",
        {
            "employees": employees,
            "shifts": shifts,
            "employee_id": employee_id,
            "start": start_str,
            "end": end_str,
        },
    )