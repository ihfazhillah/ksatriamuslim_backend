from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ksatria_muslim.events.di import event_composition_root


@api_view(["GET"])
@permission_classes([AllowAny()])
def get_current_event(request):
    current_event = event_composition_root.get_current_event_query.get_current()
    return Response(current_event)


@api_view(["GET"])
@permission_classes([AllowAny()])
def get_upcoming_events(request):
    upcoming_events = event_composition_root.get_upcoming_events_query.get_upcoming_events(limit=5)
    return Response(upcoming_events)
