from django.utils import timezone
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ksatria_muslim.events.di import event_composition_root
from ksatria_muslim.events.models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("id", "title", "description", "image")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_events(request):
    # need date, month
    date = request.query_params.get("date", None)
    month = request.query_params.get("month", None)
    if not month:
        month = timezone.localdate().month

    # default masehi, because that's the datetime package's default
    date_type = request.query_params.get("type", "masehi")

    # and type requested
    if not date:
        events = Event.objects.filter(date_type=date_type, month=month)
    else:
        events = Event.objects.filter(date_type=date_type, month=month, date=date)

    return Response({"events": EventSerializer(events, many=True).data})

