import datetime

import freezegun
import pytest
import pytz

from ksatria_muslim.events.queries.get_current_event import GetCurrentEvent
from ksatria_muslim.events.tests.factories import EventFactory

"""
event sekarang adalah:
1. event yang akan berjalan 30 menit lagi
2. event yang sedang berjalan
3. event yang sudah berjalan 30 menit yang lalu
"""

@pytest.mark.django_db
class TestGetCurrentEvent:
    SUT = None
    event_1 = None
    event_2 = None

    def setup_method(self, method):
        self.SUT = GetCurrentEvent()

        event_1_started_at = datetime.datetime(2023, 1, 10, 6, tzinfo=pytz.timezone("Asia/Jakarta"))
        self.event_1 = EventFactory(
            started_at=event_1_started_at
        )

        event_2_started_at = datetime.datetime(2023, 1, 10, 9, tzinfo=pytz.timezone("Asia/Jakarta"))
        self.event_2 = EventFactory(
            started_at=event_2_started_at
        )

    def teardown_method(self, method):
        self.event_1.delete()
        self.event_2.delete()

    @freezegun.freeze_time("2023-01-10 05:00 WIB")
    def test_no_current_event(self):
        assert not self.SUT.get_current_event()["event"]

    @freezegun.freeze_time("2023-01-10 05:30 WIB")
    def test_before_30_minutes_of_first_event_returns_it(self):
        assert self.SUT.get_current_event()["event"]["id"] == self.event_1.id
