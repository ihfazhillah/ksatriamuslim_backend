from django.utils import timezone

from ksatria_muslim.events.models import Event
from ksatria_muslim.events.serializers.event import serialize_event_list_item


class GetUpcomingEvents:
    def get_upcoming_events(self, limit=None):
        now = timezone.now()
        events = Event.objects.filter(
            started_at__gte=now
        ).order_by("started_at")

        if limit:
            events = events[:limit]

        return {
            "events": [serialize_event_list_item(event) for event in events]
        }
