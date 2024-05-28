from django.urls import path

from ksatria_muslim.events.views import get_events

app_name = "events"


urlpatterns = [
    path("", get_events, name="list"),
]
