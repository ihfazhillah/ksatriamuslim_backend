from django.core.paginator import Paginator
from django.utils import timezone

from ksatria_muslim.events.models import Event
from ksatria_muslim.events.serializers.event import serialize_event_list_item


class GetUpcomingEvents:
    def get_upcoming_events(self, limit=None, page=1):
        now = timezone.now()
        events = Event.objects.filter(
            started_at__gte=now
        ).order_by("started_at")

        has_next = False

        if limit:
            paginator = Paginator(events, per_page=limit, allow_empty_first_page=True)
            page_object = paginator.get_page(page)
            events = page_object.object_list
            has_next = page_object.has_next()

        return {
            "events": [serialize_event_list_item(event) for event in events],
            "page": page,
            "has_next": has_next
        }
