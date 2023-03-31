from django.urls import path

from ksatria_muslim.events.views import get_current_event

app_name = "events"


urlpatterns = [
    path("current/", get_current_event, name="current"),
]
