from django.urls import path

from .views import EventListView, EventRegisterView

urlpatterns = [
    path("", EventListView.as_view(), name="events-list"),
    path(
        "<uuid:event_id>/register",
        EventRegisterView.as_view(),
        name="user-register-for-event",
    ),
]
