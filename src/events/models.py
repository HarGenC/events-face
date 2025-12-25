import uuid

from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
User = get_user_model()


class Venue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_id = models.UUIDField(null=True, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Event(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_id = models.UUIDField(null=True, unique=True)
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.OPEN
    )
    venue = models.ForeignKey(
        Venue, null=True, blank=True, on_delete=models.SET_NULL, related_name="events"
    )

    def __str__(self):
        return f"{self.name} ({self.date})"


class Registration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)


class OutboxMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    topic = models.CharField(max_length=255)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True)
