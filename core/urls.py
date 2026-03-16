"""
Core URL Routing

Maps URL paths to views for:
- employee clock-in and clock-out flow
- employee meal break
- employee timesheet
- admin portal schedule and policy controls
- admin timesheets view
"""

from django.urls import path
from . import views

urlpatterns = [
    # Public landing page
    path("", views.landing, name="landing"),

    # Employee dashboard and actions
    path("dashboard/", views.home, name="home"),
    path("timesheet/", views.timesheet, name="timesheet"),
    path("clock-in/", views.clock_in, name="clock_in"),
    path("clock-out/", views.clock_out, name="clock_out"),
    path("meal-break/", views.meal_break_toggle, name="meal_break"),

    # Admin portal
    path("portal/", views.portal_home, name="portal_home"),
    path("portal/schedule/", views.admin_schedule, name="admin_schedule"),
    path("portal/timesheets/", views.admin_timesheets, name="admin_timesheets"),
]