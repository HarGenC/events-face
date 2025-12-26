import random
import uuid

from django.db import transaction

from events.models import OutboxMessage, Registration
from src.core.settings import NOTIFICATIONS_API


def create_registration(registration_data):
    with transaction.atomic():
        # Сохраняем регистрацию
        registration = Registration.objects.create(**registration_data)
        # Сохраняем сообщение в outbox
        message_id = uuid.uuid4()

        OutboxMessage.objects.create(
            id=message_id,
            topic="order_created",
            payload={
                "id": str(message_id),
                "owner_id": str(NOTIFICATIONS_API["OWNER_ID"]),
                "email": str(registration_data["email"]),
                "message": str(random.randint(1000, 9999)),
            },
        )
    return registration
