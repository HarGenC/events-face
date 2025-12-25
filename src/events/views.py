from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from events.services import create_registration

from .models import Event
from .serializers import EventSerializer, RegistrationSerializer


class EventFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Event
        fields = ["name", "status"]


class EventListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EventSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_class = EventFilter
    ordering_fields = ["date"]

    def get_queryset(self):
        qs = Event.objects.filter(status=Event.Status.OPEN).select_related("venue")
        return qs


class EventRegisterView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)

        serializer = RegistrationSerializer(
            data=request.data,
            context={"event": event},
        )
        user = request.user

        serializer.is_valid(raise_exception=True)

        valid_data = {
            "full_name": serializer.data["full_name"],
            "email": serializer.data["email"],
            "event": event,
            "user": user,
        }
        result = create_registration(valid_data)

        if result is None:
            return Response({"error": "Unsuccesfullt registered"}, status=422)
        return Response({"message": "Succesfully registered"}, status=201)
