from ksatria_muslim.events.queries.get_current_event import GetCurrentEvent


"""
event sekarang adalah:
1. event yang akan berjalan 30 menit lagi
2. event yang sedang berjalan
3. event yang sudah berjalan 30 menit yang lalu
"""
class TestGetCurrentEvent:
    SUT = None

    def setup_method(self, method):
        self.SUT = GetCurrentEvent()


    def teardown_method(self, method):
        pass


    def _create_events(self):
        pass
