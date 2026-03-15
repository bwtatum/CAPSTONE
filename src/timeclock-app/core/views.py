"""
Core Views for TimeClock

Views are intentionally thin and delegate business rules to services.py.

This keeps:
- request handling in views
- business logic in services
- persistence rules in models
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse

from . import services
from .models import WorkShift, ScheduledShift, TimeclockPolicy
from .permissions import portal_admin_required
from .policy_forms import TimeclockPolicyForm
from .schedule_forms import ScheduledShiftForm

from openpyxl import Workbook
from openpyxl.styles import Font



def landing(request):
    """
    Public landing page.
    """
    return render(request, "core/landing.html")


@login_required
@portal_admin_required
def portal_home(request):
    """
    Admin portal landing page.
    """
    return render(request, "core/portal_home.html")


@login_required
@portal_admin_required
def admin_schedule(request):
    """
    Admin portal page for:
    - Editing global policy
    - Creating and updating schedules

    The POST action determines which form is being submitted.
    """
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

                # update_or_create supports one schedule per employee per date
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
    """
    Employee view of recent shifts.

    Currently shows last 14 shifts for the logged in user.
    """
    shifts = WorkShift.objects.filter(employee=request.user).order_by("-clock_in")[:14]
    return render(request, "core/timesheet.html", {"shifts": shifts})


@login_required
def home(request):
    """
    Employee dashboard view.

    Displays the current open shift if one exists.
    """
    current_shift = services.get_open_shift(request.user)
    return render(request, "core/home.html", {"current_shift": current_shift})


@login_required
def clock_in(request):
    """
    POST endpoint to clock the logged in user in.

    Uses services.clock_in for all validation and record creation.
    """
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
    """
    POST endpoint to clock the logged in user out.

    Uses services.clock_out for all validation and record updates.
    """
    if request.method != "POST":
        return redirect("home")

    ok, msg = services.clock_out(request.user)
    if ok:
        messages.success(request, msg)
    else:
        messages.error(request, msg)
    return redirect("home")


@login_required
@portal_admin_required
def download_timesheets(request):
    """
    Admin-only endpoint that returns a .txt file of all closed shifts
    for every employee, grouped by employee and ordered by clock-in time.
    """
    shifts = WorkShift.objects.select_related("employee").exclude(
        clock_out__isnull=True
    ).order_by("employee__username", "clock_in")

    lines = ["EMPLOYEE TIMESHEETS\n", "=" * 40 + "\n\n"]

    current_employee = None
    for shift in shifts:
        emp_name = shift.employee.get_full_name() or shift.employee.username

        if emp_name != current_employee:
            if current_employee is not None:
                lines.append("\n")
            lines.append(f"Employee: {emp_name}\n")
            lines.append("-" * 30 + "\n")
            current_employee = emp_name

        clock_in_str  = shift.clock_in.strftime("%Y-%m-%d %I:%M %p")
        clock_out_str = shift.clock_out.strftime("%Y-%m-%d %I:%M %p")
        total         = str(shift.total_time) if shift.total_time else "N/A"

        lines.append(f"  Clock In:   {clock_in_str}\n")
        lines.append(f"  Clock Out:  {clock_out_str}\n")
        lines.append(f"  Total Time: {total}\n\n")

    response = HttpResponse("".join(lines), content_type="text/plain")
    response["Content-Disposition"] = 'attachment; filename="timesheets.txt"'
    return response


@login_required
@portal_admin_required
def download_timesheets_excel(request):
    """
    Admin-only endpoint that returns an Excel file of all closed shifts
    for every employee, grouped by employee and ordered by clock-in time.
    """

    shifts = WorkShift.objects.select_related("employee").exclude(
        clock_out__isnull=True
    ).order_by("employee__username", "clock_in")


    wb = Workbook()
    ws = wb.active
    ws.title = "Timesheets"
    headers = ["Employee Name", "Clock In", "Clock Out", "Total Time"]
    ws.append(headers)

    for cell in ws[1]:
        cell.font = Font(bold=True)

    for shift in shifts:
        emp_name = shift.employee.get_full_name() or shift.employee.username
        total = str(shift.total_time) if shift.total_time else "N/A"

        ws.append([
            emp_name,
            shift.clock_in.strftime("%Y-%m-%d %I:%M %p"),
            shift.clock_out.strftime("%Y-%m-%d %I:%M %p"),
            total
        ])

    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        ws.column_dimensions[column_letter].width = max_length + 2

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="timesheets.xlsx"'

    wb.save(response)
    return response
