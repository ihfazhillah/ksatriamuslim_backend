from django.utils import timezone
from rest_framework import serializers

from ksatria_muslim.events.models import Event


class EventSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    presenter = serializers.SerializerMethodField()
    organizer = serializers.SerializerMethodField()

    _date_fmt = "%A, %d %B %Y"
    _time_fmt = "%H:%M %Z"

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "thumbnail",
            "presenter",
            "organizer",
            "date",
            "time",
            "youtube_link",
            "zoom_link",
        )

    def get_date(self, obj: Event):
        str_date = self._localized_started_at(obj.started_at).strftime(self._date_fmt)
        return str_date

    def get_time(self, obj: Event):
        str_time = self._localized_started_at(obj.started_at).strftime(self._time_fmt)
        return str_time

    def get_organizer(self, obj: Event):
        return obj.organizer.title

    def get_presenter(self, obj: Event):
        return obj.presenter.get_full_name()

    def _localized_started_at(self, started_at):
        return timezone.localtime(started_at)


def serialize_event(event):
    if not event:
        return

    serializer = EventSerializer(instance=event)
    return serializer.data
