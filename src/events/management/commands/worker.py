import time
from datetime import datetime, timezone

import requests
from django.core.management.base import BaseCommand
from django.db import transaction

from events.models import OutboxMessage
from src.core.settings import NOTIFICATIONS_API


class Command(BaseCommand):
    help = "Create outboxmessage worker"

    def handle(self, *args, **options):
        url = NOTIFICATIONS_API["URL"]
        while True:
            print("start check")
            with transaction.atomic():
                # Получаем неотправленные сообщения
                messages = (
                    OutboxMessage.objects.filter(sent=False)
                    .select_for_update(skip_locked=True)
                    .order_by("created_at")[:100]
                )

                for msg in messages:
                    try:
                        response = requests.post(
                            url,
                            headers={
                                "Authorization": f"Bearer {NOTIFICATIONS_API['TOKEN']}",
                                "Content-Type": "application/json",
                            },
                            json=msg.payload,
                            timeout=10,
                        )
                        print("I'm here")
                        print(msg.payload)
                        print(response.status_code)
                        if response.status_code in (201, 409):
                            print("I'm here too")
                            msg.sent = True
                            msg.sent_at = datetime.now(timezone.utc)
                            msg.save()
                            print("Сообщение было сохранено")
                    except Exception as e:
                        print(f"Failed to process message {msg.id}: {e}")
            time.sleep(1)
