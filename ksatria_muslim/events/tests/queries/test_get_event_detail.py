import datetime

import pytest
import pytz

from ksatria_muslim.events.queries.get_event_detail import GetEventDetail
from ksatria_muslim.events.tests.factories import EventFactory


@pytest.mark.django_db
class TestGetEventDetail:
    sut = None
    event_1 = None

    def setup_method(self, method):
        self.sut = GetEventDetail()
        tz = pytz.timezone("Asia/Jakarta")

        event_1_started_at = datetime.datetime(2023, 1, 10, 6)
        event_1_started_at.replace(tzinfo=tz)
        self.event_1 = EventFactory(
            started_at=event_1_started_at
        )

    def test_event_not_found_returns_null_event(self):
        resp = self.sut.get_event(-1)
        assert resp["event"] is None

    def test_event_found(self):
        resp = self.sut.get_event(self.event_1.id)
        assert resp["event"]["id"] == self.event_1.id



