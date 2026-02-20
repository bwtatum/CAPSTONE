"""
Core App Tests

Tests core business rules implemented in services.py:
- strict schedule enforcement
- non strict schedule behavior
- grace window boundaries
- one open shift per employee
- clock out behavior
- portal admin access decorator
"""

from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.test import TestCase, RequestFactory
from django.utils import timezone

from . import services
from .models import TimeclockPolicy, ScheduledShift, WorkShift
from .permissions import portal_admin_required

User = get_user_model()


class BaseTimeclockTestCase(TestCase):
    """
    Shared setup helpers for timeclock tests.
    """

    def setUp(self):
        self.employee = User.objects.create_user(username="employee1", password="pass12345")
        self.admin = User.objects.create_user(username="admin1", password="pass12345")

        self.admin_group, _ = Group.objects.get_or_create(name="Admin")
        self.admin.groups.add(self.admin_group)

        policy = TimeclockPolicy.get_solo()
        policy.strict_schedule_enforced = True
        policy.allow_unscheduled_clock_in_when_not_strict = True
        policy.grace_minutes_before_start = 0
        policy.grace_minutes_after_start = 0
        policy.allow_admin_time_edits = True
        policy.require_admin_edit_reason = True
        policy.save()

    def create_schedule_for_today(self, user=None, start=time(9, 0), end=time(17, 0), canceled=False, notes=""):
        """
        Creates a ScheduledShift for localdate().
        """
        user = user or self.employee
        return ScheduledShift.objects.create(
            employee=user,
            date=timezone.localdate(),
            start_time=start,
            end_time=end,
            is_canceled=canceled,
            notes=notes,
        )


class ClockInServiceTests(BaseTimeclockTestCase):
    def test_clock_in_strict_requires_schedule(self):
        policy = TimeclockPolicy.get_solo()
        policy.strict_schedule_enforced = True
        policy.save()

        ok, msg = services.clock_in(self.employee)
        self.assertFalse(ok)
        self.assertIn("No scheduled shift today", msg)
        self.assertEqual(WorkShift.objects.count(), 0)

    def test_clock_in_strict_allows_with_schedule(self):
        self.create_schedule_for_today()

        ok, msg = services.clock_in(self.employee)
        self.assertTrue(ok)
        self.assertIn("Clocked in", msg)

        shift = WorkShift.objects.get(employee=self.employee)
        self.assertIsNotNone(shift.scheduled_shift)
        self.assertEqual(shift.status, WorkShift.Status.OPEN)

    def test_clock_in_prevents_multiple_open_shifts(self):
        self.create_schedule_for_today()
        ok1, _ = services.clock_in(self.employee)
        self.assertTrue(ok1)

        ok2, msg2 = services.clock_in(self.employee)
        self.assertFalse(ok2)
        self.assertIn("already have an open shift", msg2)
        self.assertEqual(WorkShift.objects.count(), 1)

    def test_clock_in_non_strict_flags_unscheduled(self):
        policy = TimeclockPolicy.get_solo()
        policy.strict_schedule_enforced = False
        policy.allow_unscheduled_clock_in_when_not_strict = True
        policy.save()

        ok, msg = services.clock_in(self.employee)
        self.assertTrue(ok)
        self.assertIn("flagged", msg)

        shift = WorkShift.objects.get(employee=self.employee)
        self.assertIsNone(shift.scheduled_shift)
        self.assertEqual(shift.status, WorkShift.Status.FLAGGED)

    def test_clock_in_non_strict_blocks_unscheduled_when_disabled(self):
        policy = TimeclockPolicy.get_solo()
        policy.strict_schedule_enforced = False
        policy.allow_unscheduled_clock_in_when_not_strict = False
        policy.save()

        ok, msg = services.clock_in(self.employee)
        self.assertFalse(ok)
        self.assertIn("Unscheduled clock in not allowed", msg)
        self.assertEqual(WorkShift.objects.count(), 0)

    def test_clock_in_strict_grace_window_blocks_outside_window(self):
        policy = TimeclockPolicy.get_solo()
        policy.strict_schedule_enforced = True
        policy.grace_minutes_before_start = 5
        policy.grace_minutes_after_start = 5
        policy.save()

        now = timezone.localtime()

        # Schedule start is far from now so clock in should be outside grace window
        future_start = (now + timedelta(hours=2)).time().replace(second=0, microsecond=0)
        self.create_schedule_for_today(start=future_start, end=time(23, 0))

        ok, msg = services.clock_in(self.employee)
        self.assertFalse(ok)
        self.assertIn("outside allowed time window", msg)
        self.assertEqual(WorkShift.objects.count(), 0)

    def test_clock_in_strict_grace_window_allows_inside_window(self):
        policy = TimeclockPolicy.get_solo()
        policy.strict_schedule_enforced = True
        policy.grace_minutes_before_start = 10
        policy.grace_minutes_after_start = 10
        policy.save()

        now = timezone.localtime()

        # Start within 5 minutes of now which is inside 10 minute grace
        start_close = (now + timedelta(minutes=5)).time().replace(second=0, microsecond=0)
        self.create_schedule_for_today(start=start_close, end=time(23, 0))

        ok, msg = services.clock_in(self.employee)
        self.assertTrue(ok)
        self.assertIn("Clocked in", msg)
        self.assertEqual(WorkShift.objects.count(), 1)


class ClockOutServiceTests(BaseTimeclockTestCase):
    def test_clock_out_fails_when_no_open_shift(self):
        ok, msg = services.clock_out(self.employee)
        self.assertFalse(ok)
        self.assertIn("No open shift", msg)

    def test_clock_out_closes_open_shift(self):
        self.create_schedule_for_today()
        ok_in, _ = services.clock_in(self.employee)
        self.assertTrue(ok_in)

        ok_out, msg_out = services.clock_out(self.employee)
        self.assertTrue(ok_out)
        self.assertIn("Clocked out", msg_out)

        shift = WorkShift.objects.get(employee=self.employee)
        self.assertIsNotNone(shift.clock_out)
        self.assertEqual(shift.status, WorkShift.Status.CLOSED)

    def test_clock_out_does_not_override_flagged_status(self):
        policy = TimeclockPolicy.get_solo()
        policy.strict_schedule_enforced = False
        policy.allow_unscheduled_clock_in_when_not_strict = True
        policy.save()

        ok_in, _ = services.clock_in(self.employee)
        self.assertTrue(ok_in)

        shift = WorkShift.objects.get(employee=self.employee)
        self.assertEqual(shift.status, WorkShift.Status.FLAGGED)

        ok_out, _ = services.clock_out(self.employee)
        self.assertTrue(ok_out)

        shift.refresh_from_db()
        self.assertIsNotNone(shift.clock_out)
        self.assertEqual(shift.status, WorkShift.Status.FLAGGED)


class PortalPermissionTests(BaseTimeclockTestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()

    def test_portal_admin_required_denies_non_admin(self):
        @portal_admin_required
        def dummy_view(request):
            return "ok"

        request = self.factory.get("/portal/")
        request.user = self.employee

        with self.assertRaises(PermissionDenied):
            dummy_view(request)

    def test_portal_admin_required_allows_admin(self):
        @portal_admin_required
        def dummy_view(request):
            return "ok"

        request = self.factory.get("/portal/")
        request.user = self.admin

        result = dummy_view(request)
        self.assertEqual(result, "ok")
