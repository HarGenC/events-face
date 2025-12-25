import random
import uuid

from django.db import transaction

from events.models import OutboxMessage, Registration

# В следующем коммите спрячу в .env
owner_id = "a1a4fb29-2a76-47d9-9965-d386aa8ba650"


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
                "owner_id": str(owner_id),
                "email": str(registration_data["email"]),
                "message": str(random.randint(1000, 9999)),
            },
        )
    return registration
