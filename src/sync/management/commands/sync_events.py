from datetime import datetime

from django.core.management.base import BaseCommand

from sync.models import SyncLog
from sync.services import sync_events


class Command(BaseCommand):
    help = "Sync events from events-provider"

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Run full synchronization",
        )
        parser.add_argument(
            "--date",
            type=str,
            help="Sync from specific date (YYYY-MM-DD)",
        )

    def handle(self, *args, **options):
        full = options["all"]
        date_arg = options.get("date")

        changed_at = None

        if full:
            self.stdout.write("Running full sync...")
            created, updated = sync_events(full_sync=True)
            self.stdout.write(
                self.style.SUCCESS(f"Done: created={created}, updated={updated}")
            )
            return

        if date_arg:
            changed_at = datetime.fromisoformat(date_arg)
        else:
            last_log = SyncLog.objects.order_by("run_at").first()
            if last_log is not None:
                changed_at = last_log.run_at

        self.stdout.write(f"Running incremental sync from: {changed_at}")
        created, updated = sync_events(changed_at=changed_at)
        self.stdout.write(
            self.style.SUCCESS(f"Done: created={created}, updated={updated}")
        )
