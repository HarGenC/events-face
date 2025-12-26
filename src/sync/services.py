import time
from datetime import datetime, timezone

import requests
from django.utils.dateparse import parse_datetime

from events.models import Event, Venue
from src.core.settings import PROVIDER_API

from .models import SyncLog

def fetch_events(url: str = PROVIDER_API["URL"], changed_at: datetime | None = None):
    """Возвращает список мероприятий с внешнего API."""
    params = {}
    if changed_at:
        params["changed_at"] = changed_at.date().isoformat()

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {PROVIDER_API["TOKEN"]}",
            "Content-Type": "application/json",
        },
        params=params,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def sync_events(changed_at: datetime | None = None, full_sync: bool = False):
    """Основная функция синхронизации."""
    start = time.perf_counter()
    if full_sync:
        raw_data = fetch_events()
    else:
        raw_data = fetch_events(changed_at=changed_at)

    created = 0
    updated = 0

    current_date = datetime.now(timezone.utc)

    while True:
        events_data = raw_data["results"]

        for item in events_data:
            ext_id = item["id"]

            if datetime.fromisoformat(item["registration_deadline"]) > current_date:
                status = Event.Status.OPEN
            else:
                status = Event.Status.CLOSED

            event, created_flag = Event.objects.update_or_create(
                external_id=ext_id,
                defaults={
                    "name": item["name"],
                    "date": parse_datetime(item["event_time"]),
                    "status": status,
                    "venue": get_or_create_venue(item["place"]),
                },
            )

            if created_flag:
                created += 1
            else:
                updated += 1

        if raw_data["next"] is None:
            break

        raw_data = fetch_events(raw_data["next"])

    SyncLog.objects.create(
        time_execution=start - time.perf_counter(),
        created_count=created,
        updated_count=updated,
    )

    return created, updated


def get_or_create_venue(venue_data):
    """Обрабатывает площадку, если она есть."""
    if not venue_data:
        return None

    venue, _ = Venue.objects.update_or_create(
        external_id=venue_data["id"],
        defaults={"name": venue_data["name"]},
    )
    return venue
