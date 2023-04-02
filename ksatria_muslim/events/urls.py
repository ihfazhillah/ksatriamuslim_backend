from django.urls import path

from ksatria_muslim.events.views import get_current_event, get_upcoming_events, get_event_detail

app_name = "events"


urlpatterns = [
    path("current/", get_current_event, name="current"),
    path("upcoming/", get_upcoming_events, name="upcoming"),
    path("<event_id>/", get_event_detail, name="detail"),
]
