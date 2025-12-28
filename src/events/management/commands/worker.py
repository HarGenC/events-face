import logging
import time
from datetime import datetime, timezone

import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from rest_framework import status

from events.models import OutboxMessage
from src.core.settings import NOTIFICATIONS_API

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "run outboxmessage worker"

    def handle(self, *args, **options):
        url = NOTIFICATIONS_API["URL"]
        while True:
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
                        if response.status_code in (
                            status.HTTP_201_CREATED,
                            status.HTTP_409_CONFLICT,
                        ):
                            msg.sent = True
                            msg.sent_at = datetime.now(timezone.utc)
                            msg.save()
                            logger.info("Сообщение {msg.id} было сохранено")
                    except Exception as e:
                        logger.error(f"Failed to process message {msg.id}: {e}")
            time.sleep(1)
