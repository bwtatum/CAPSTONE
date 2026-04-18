import csv
import os
import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from core.models import ScheduledShift

User = get_user_model()


class Command(BaseCommand):
    help = "Inject shifts via CSV or generate random schedules"

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            nargs='?',
            type=str,
            help='Optional CSV file (username,start_time,end_time)'
        )

        parser.add_argument(
            '--count',
            type=int,
            help='Generate N random shifts'
        )

        parser.add_argument(
            '--user',
            type=str,
            help='Generate shifts for a specific username'
        )

        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Spread generated shifts across N days (default: 7)'
        )

        parser.add_argument(
            '--night-only',
            action='store_true',
            help='Generate only night shifts (6PM+)'
        )

    def handle(self, *args, **kwargs):
        count = kwargs.get('count')
        file_path = kwargs.get('csv_file')
        username = kwargs.get('user')
        days = kwargs.get('days')
        night_only = kwargs.get('night_only')

        created_count = 0
        skipped_count = 0

        # 🎲 RANDOM GENERATION MODE
        if count:
            if username:
                try:
                    users = [User.objects.get(username=username)]
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"User not found: {username}"))
                    return
            else:
                users = list(User.objects.all())

            if not users:
                self.stdout.write(self.style.ERROR("No users available."))
                return

            base_date = datetime.now()

            for _ in range(count):
                try:
                    user = random.choice(users)

                    shift_day = base_date + timedelta(days=random.randint(0, days))

                    if night_only:
                        start_hour = random.choice([18, 19, 20])
                    else:
                        start_hour = random.choice([6, 7, 8, 18, 19, 20])

                    start_time = shift_day.replace(
                        hour=start_hour, minute=0, second=0, microsecond=0
                    )

                    duration = random.choice([8, 9, 10])
                    end_time = start_time + timedelta(hours=duration)

                    ScheduledShift.objects.update_or_create(
                        employee=user,
                        date=start_time.date(),
                        defaults={
                            "start_time": start_time,
                            "end_time": end_time,
                        }
                    )

                    created_count += 1

                except Exception as e:
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(
                        f"Skipped random shift | Error: {e}"
                    ))

            self.stdout.write(self.style.SUCCESS(
                f"Generated {created_count} shifts. Skipped {skipped_count}."
            ))
            return

        # 📄 CSV MODE
        if file_path:
            if not os.path.exists(file_path):
                self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
                return

            with open(file_path, newline='') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    try:
                        user = User.objects.get(username=row['username'])

                        start_time = datetime.strptime(row['start_time'], "%Y-%m-%d %H:%M")
                        end_time = datetime.strptime(row['end_time'], "%Y-%m-%d %H:%M")

                        ScheduledShift.objects.update_or_create(
                            employee=user,
                            date=start_time.date(),
                            defaults={
                                "start_time": start_time,
                                "end_time": end_time,
                            }
                        )

                        created_count += 1

                    except Exception as e:
                        skipped_count += 1
                        self.stdout.write(self.style.WARNING(
                            f"Skipped row {row} | Error: {e}"
                        ))

            self.stdout.write(self.style.SUCCESS(
                f"CSV import complete. Processed {created_count}, skipped {skipped_count}."
            ))
            return

        # ❌ No args provided
        self.stdout.write(self.style.ERROR(
            "Provide either a CSV file or use --count"
        ))
