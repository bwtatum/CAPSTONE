import csv
import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from core.models import ScheduledShift

User = get_user_model()


class Command(BaseCommand):
    help = "Inject scheduled shifts into the database from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['csv_file']

        # ✅ Check file exists
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(
                f"File not found: {file_path}"
            ))
            return

        created_count = 0
        skipped_count = 0

        with open(file_path, newline='') as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    user = User.objects.get(username=row['username'])

                    start_time = datetime.strptime(
                        row['start_time'], "%Y-%m-%d %H:%M"
                    )
                    end_time = datetime.strptime(
                        row['end_time'], "%Y-%m-%d %H:%M"
                    )

                    # ✅ Update if exists, create if not
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
            f"Done. Processed {created_count} rows. Skipped {skipped_count}."
        ))