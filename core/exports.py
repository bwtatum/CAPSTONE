# core/exports.py
import csv
import io
from datetime import date
from django.utils import timezone
from .models import WorkShift

def _seconds_between(start, end):
    if start is None:
        return 0
    if end is None:
        end = timezone.now()
    delta = end - start
    return max(0, int(delta.total_seconds()))

def _seconds_from_breaks(shift):
    total = 0
    # expects related_name 'meal_breaks' on MealBreak FK to WorkShift
    for br in getattr(shift, "meal_breaks", []).all():
        total += _seconds_between(br.start_time, br.end_time)
    return total

def _format_hhmm(total_seconds):
    """Return H:MM (hours no leading zero, minutes two digits)."""
    total_seconds = int(max(0, total_seconds))
    minutes = total_seconds // 60
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}:{mins:02d}"

def _format_human_datetime(dt):
    """
    Format datetimes like: 'March 9, 2026, 2:16 p.m.'
    Uses local timezone and produces lowercase 'a.m.' / 'p.m.' with no leading zeros.
    """
    if not dt:
        return ""
    dt_local = timezone.localtime(dt)
    month = dt_local.strftime("%B")
    day = dt_local.day  # no leading zero
    year = dt_local.year
    minute = dt_local.minute
    hour_24 = dt_local.hour
    hour_12 = hour_24 % 12 or 12
    meridiem = "a.m." if hour_24 < 12 else "p.m."
    return f"{month} {day}, {year}, {hour_12}:{minute:02d} {meridiem}"

def get_workshift_queryset(employee=None, start_date: date = None, end_date: date = None, max_rows: int = None):
    qs = WorkShift.objects.select_related("employee").prefetch_related("meal_breaks").order_by("-clock_in")
    if employee:
        qs = qs.filter(employee=employee)
    if start_date:
        qs = qs.filter(clock_in__date__gte=start_date)
    if end_date:
        qs = qs.filter(clock_in__date__lte=end_date)
    if max_rows:
        return qs[:max_rows]
    return qs

def export_workshifts_csv_bytes(employee=None, start_date: date = None, end_date: date = None, max_rows: int = None):
    """
    Return CSV as bytes. Columns match the UI:
    Clock in, Clock out, Break, Total, Worked, Status
    """
    qs = get_workshift_queryset(employee=employee, start_date=start_date, end_date=end_date, max_rows=max_rows)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Clock in", "Clock out", "Break", "Total", "Worked", "Status"])

    for shift in qs:
        ci = shift.clock_in
        co = shift.clock_out

        total_seconds = _seconds_between(ci, co)
        break_seconds = _seconds_from_breaks(shift)
        worked_seconds = max(0, total_seconds - break_seconds)

        writer.writerow([
            _format_human_datetime(ci) if ci else "",
            _format_human_datetime(co) if co else "",
            _format_hhmm(break_seconds),
            _format_hhmm(total_seconds),
            _format_hhmm(worked_seconds),
            shift.status,
        ])

    return output.getvalue().encode("utf-8")