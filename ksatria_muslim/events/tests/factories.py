import datetime

from factory import SubFactory, Sequence
from factory.django import DjangoModelFactory, ImageField
from factory.fuzzy import FuzzyDateTime
from pytz import UTC

from ksatria_muslim.books.tests.factories import UserFactory
from ksatria_muslim.events.models import Event, EventOrganizer


class EventOrganizerFactory(DjangoModelFactory):
    class Meta:
        model = EventOrganizer

    title = Sequence(lambda n: "Event Organizer %03d" % n)


class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event

    presenter = SubFactory(UserFactory)
    submitter = SubFactory(UserFactory)
    organizer = SubFactory(EventOrganizerFactory)

    title = Sequence(lambda n: "Kajian Anak %03d" % n)
    thumbnail = ImageField()
    started_at = FuzzyDateTime(datetime.datetime(2023, 1, 1, tzinfo=UTC))

