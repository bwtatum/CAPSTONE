import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import ScheduledShift

User = get_user_model()

class Command(BaseCommand):
    help = "Import scheduled shifts from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['csv_file']

        created_count = 0
        skipped_count = 0

        with open(file_path, newline='') as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    user = User.objects.get(username=row['username'])

                    start_time = datetime.strptime(row['start_time'], "%Y-%m-%d %H:%M")
                    end_time = datetime.strptime(row['end_time'], "%Y-%m-%d %H:%M")

                    ScheduledShift.objects.create(
                        employee=user,  # adjust if needed
                        start_time=start_time,
                        end_time=end_time
                    )

                    created_count += 1

                except Exception as e:
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(
                        f"Skipped row {row} | Error: {e}"
                    ))

        self.stdout.write(self.style.SUCCESS(
            f"Done. Created {created_count} shifts. Skipped {skipped_count}."
        ))
