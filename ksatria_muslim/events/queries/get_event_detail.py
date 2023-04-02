import datetime

from django.db import models
from django.utils import timezone

from ksatria_muslim.events.models import Event
from ksatria_muslim.events.serializers.event import serialize_event


class GetEventDetail:
    def get_event(self, event_id):
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            event = None

        return {"event": serialize_event(event)}
