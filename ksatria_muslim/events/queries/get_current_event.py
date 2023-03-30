import datetime

from django.db import models
from django.utils.timezone import localtime

from ksatria_muslim.events.models import Event


def serialize_event(event):
    if not event:
        return

    return {"id": event.id}


class GetCurrentEvent:
    def get_current_event(self):
        now_local = localtime()
        events = Event.objects.all().annotate(
            diff_1=models.F("started_at") - models.Value(now_local)
        ).filter(
            diff_1__lte=datetime.timedelta(minutes=30)
        )

        event = events.first()

        return {"event": serialize_event(event)}
