import time
from datetime import datetime, timezone

import requests
from django.core.management.base import BaseCommand
from django.db import transaction

from events.models import OutboxMessage

# В следующем коммите спрячу в .env
TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc19zdGFmZiI6ZmFsc2UsInN1YiI6IjMyIiwiZXhwIjoxNzY2NzgxMjAxLCJpYXQiOjE3NjY2OTQ4MDF9.a9RlvDN6casiPTqe6pqGY1Rkr4dmblj5q20cAPuBzCyb5ClBmRKgMVdAcszdgv1dXWM4A3drNuscXerA8oVwpfI0bGR0XhkPWyNzZuqGu7m0kcbqMTyRgpVCzgb9dY6EczI5LOJh48qyrhP1YiLgRkVfLxvAJHF_kkFXEIUbbHCGFAsxizkT-vylrXm0JDfn_o4jmVWwI4OYic0U7wbQIW4rwQryTXx9cz2bmLsDbDn0UIAqUzmyy4WzmkZPGEd0Ri6twbJwK6K8eW3nqT4CPAfBb0c7wFCezzMNyq34eDmV1DnEzQCokNxUGcHka4APcJzmQ-Xr4rU-2MSPw7_UMA"


class Command(BaseCommand):
    help = "Create outboxmessage worker"

    def handle(self, *args, **options):
        url = "https://notifications.k3scluster.tech/api/notifications"
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
                                "Authorization": f"Bearer {TOKEN}",
                                "Content-Type": "application/json",
                            },
                            json=msg.payload,
                            timeout=10,
                        )
                        if response.status_code in (201, 409):
                            msg.sent = True
                            msg.sent_at = datetime.now(timezone.utc)
                            msg.save()
                            print("Сообщение было сохранено")
                    except Exception as e:
                        print(f"Failed to process message {msg.id}: {e}")
            time.sleep(1)
