from ksatria_muslim.events.queries.get_current_event import GetCurrentEvent


class EventCompositionRoot:
    @property
    def get_current_event_query(self):
        return GetCurrentEvent()


event_composition_root = EventCompositionRoot()
