from ksatria_muslim.events.queries.get_current_event import GetCurrentEvent
from ksatria_muslim.events.queries.get_upcoming_events import GetUpcomingEvents


class EventCompositionRoot:
    @property
    def get_current_event_query(self):
        return GetCurrentEvent()

    @property
    def get_upcoming_events_query(self):
        return GetUpcomingEvents()


event_composition_root = EventCompositionRoot()
