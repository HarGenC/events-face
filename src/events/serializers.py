from rest_framework import serializers

from .models import Event, Registration


class EventSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source="venue.name", read_only=True)

    class Meta:
        model = Event
        fields = ["id", "name", "date", "status", "venue", "venue_name"]


class RegistrationSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=128)
    email = serializers.EmailField()

    def validate(self, attrs):
        event: Event = self.context["event"]

        if event.status != Event.Status.OPEN:
            raise serializers.ValidationError("Event is not open for registration")

        if Registration.objects.filter(
            event=event,
            email=attrs["email"],
        ).exists():
            raise serializers.ValidationError("User already registered for this event")

        return attrs
