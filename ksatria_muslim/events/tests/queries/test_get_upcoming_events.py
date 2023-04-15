import datetime

import freezegun
import pytest
import pytz

from ksatria_muslim.events.queries.get_upcoming_events import GetUpcomingEvents
from ksatria_muslim.events.tests.factories import EventFactory


@pytest.mark.django_db
class TestGetCurrentEvent:

    SUT = None
    event_1 = None
    event_2 = None

    def setup_method(self, method):
        self.SUT = GetUpcomingEvents()

        tz = pytz.timezone("Asia/Jakarta")


        event_1_started_at = datetime.datetime(2023, 1, 10, 6)
        event_1_started_at.replace(tzinfo=tz)
        self.event_1 = EventFactory(
            started_at=event_1_started_at
        )

        event_2_started_at = datetime.datetime(2023, 1, 10, 9)
        event_2_started_at.replace(tzinfo=tz)
        self.event_2 = EventFactory(
            started_at=event_2_started_at
        )

    def teardown_method(self, method):
        self.event_1.delete()
        self.event_2.delete()

    def test_get_upcoming_events_accept_limit_param(self):
        resp = self.SUT.get_upcoming_events(limit=1)
        assert isinstance(resp["events"], list)


    # test jumlah result tanpa limit
    @freezegun.freeze_time("2023-01-10 05:00 WIB")
    def test_get_upcoming_events_returns_all_upcoming(self):
        resp = self.SUT.get_upcoming_events()
        assert len(resp["events"]) == 2

    @freezegun.freeze_time("2023-01-10 05:00 WIB")
    def test_get_upcoming_events_returns_first_upcoming_serve_first(self):
        resp = self.SUT.get_upcoming_events()
        event_1 = resp["events"][0]
        event_2 = resp["events"][1]
        assert event_1["id"] == self.event_1.id
        assert event_2["id"] == self.event_2.id

    # test jumlah result dengan limit
    @freezegun.freeze_time("2023-01-10 05:00 WIB")
    def test_get_upcoming_events_with_limit(self):
        resp = self.SUT.get_upcoming_events(limit=1)
        assert len(resp["events"]) == 1
        event_1 = resp["events"][0]
        assert event_1["id"] == self.event_1.id

    # test jumlah result ketika sudah terlewat
    @freezegun.freeze_time("2023-01-10 08:00 WIB")
    def test_get_upcoming_events_with_limit(self):
        resp = self.SUT.get_upcoming_events()
        assert len(resp["events"]) == 1
        event_1 = resp["events"][0]
        assert event_1["id"] == self.event_2.id

    @freezegun.freeze_time("2023-01-10 08:00 WIB")
    def test_get_upcoming_events_response_keys(self):
        resp = self.SUT.get_upcoming_events()
        assert len(resp["events"]) == 1
        event_1 = resp["events"][0]
        expected_keys = ["id", "thumbnail", "title", "date", "time"]
        diff = set(expected_keys).difference(set(event_1.keys()))
        assert not len(diff)

    @freezegun.freeze_time("2023-01-10 08:00 WIB")
    def test_get_upcoming_events_response_date_and_time(self):
        resp = self.SUT.get_upcoming_events()
        assert len(resp["events"]) == 1
        event_1 = resp["events"][0]
        assert event_1["date"] == "Tuesday, 10 January 2023"
        assert event_1["time"] == "09:00 WIB"

    @freezegun.freeze_time("2023-01-10 05:00 WIB")
    def test_get_upcoming_events_paginated_page_1(self):
        resp = self.SUT.get_upcoming_events(limit=1)
        event_1 = resp["events"][0]
        assert event_1["id"] == self.event_1.id
        assert resp["has_next"]
        assert resp["page"] == 1

    @freezegun.freeze_time("2023-01-10 05:00 WIB")
    def test_get_upcoming_events_paginated_page_2(self):
        resp = self.SUT.get_upcoming_events(limit=1, page=2)
        event_1 = resp["events"][0]
        assert event_1["id"] == self.event_2.id
        assert not resp["has_next"]
        assert resp["page"] == 2
