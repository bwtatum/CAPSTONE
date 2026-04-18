from django.test import TestCase
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from core.models import WorkShift, MealBreak

class WorkShiftTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test_user")

    def test_create_shift(self):
        shift = WorkShift.objects.create(
            employee=self.user,
            clock_in=timezone.now(),
            clock_out=timezone.now() + timedelta(hours=8),
        )
        self.assertIsNotNone(shift.id)

    def test_shift_duration_positive(self):
        shift = WorkShift.objects.create(
            employee=self.user,
            clock_in=timezone.now(),
            clock_out=timezone.now() + timedelta(hours=8),
        )
        self.assertGreater(shift.total_seconds(), 0)

    def test_break_integrity(self):
        shift = WorkShift.objects.create(
            employee=self.user,
            clock_in=timezone.now(),
            clock_out=timezone.now() + timedelta(hours=8),
        )

        break_obj = MealBreak.objects.create(
            shift=shift,
            start_time=shift.clock_in + timedelta(hours=4),
            end_time=shift.clock_in + timedelta(hours=4, minutes=30),
        )

        self.assertGreater(break_obj.duration_seconds(), 0)
        self.assertGreater(shift.break_seconds(), 0)
