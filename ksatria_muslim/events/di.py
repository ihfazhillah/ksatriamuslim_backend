from ksatria_muslim.events.queries.get_current_event import GetCurrentEvent
from ksatria_muslim.events.queries.get_event_detail import GetEventDetail
from ksatria_muslim.events.queries.get_upcoming_events import GetUpcomingEvents


class EventCompositionRoot:
    @property
    def get_current_event_query(self):
        return GetCurrentEvent()

    @property
    def get_upcoming_events_query(self):
        return GetUpcomingEvents()

    @property
    def get_event_detail_query(self):
        return GetEventDetail()


event_composition_root = EventCompositionRoot()
