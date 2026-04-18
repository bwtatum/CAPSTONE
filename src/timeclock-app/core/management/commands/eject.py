from django.core.management.base import BaseCommand
from core.models import ScheduledShift

class Command(BaseCommand):
    help = "Delete scheduled shifts (with optional filters)"

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Filter by username')
        parser.add_argument('--all', action='store_true', help='Delete ALL shifts')

    def handle(self, *args, **kwargs):
        username = kwargs.get('username')
        delete_all = kwargs.get('all')

        queryset = ScheduledShift.objects.all()

        if username:
            queryset = queryset.filter(employee__username=username)

        if not delete_all and not username:
            self.stdout.write(self.style.ERROR(
                "You must specify --all or --username"
            ))
            return

        count = queryset.count()
        queryset.delete()

        self.stdout.write(self.style.SUCCESS(
            f"Deleted {count} scheduled shifts."
        ))
