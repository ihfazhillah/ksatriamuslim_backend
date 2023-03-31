import datetime

from django.db import models
from django.utils import timezone

from ksatria_muslim.events.models import Event
from ksatria_muslim.events.serializers.event import serialize_event


class GetCurrentEvent:
    def get_current_event(self):
        now = timezone.now()

        events = Event.objects.all().annotate(
            before_30=models.ExpressionWrapper(
                models.F("started_at") - datetime.timedelta(minutes=30),
                output_field=models.DateTimeField()
            ),
            after_30=models.ExpressionWrapper(
                models.F("started_at") + datetime.timedelta(minutes=30),
                output_field=models.DateTimeField()
            ),
        ).filter(
            before_30__lte=now,
            after_30__gte=now
        )

        event = events.first()

        return {"event": serialize_event(event)}
