from ksatria_muslim.invoice.integrations.clockify import ClockifyTimeEntry
from ksatria_muslim.invoice.models import TimeEntry, ClockifyIntegration


class Clockify:
    def __init__(self, integration: ClockifyIntegration):
        self._integration = integration

    def time_entry_to_django(self, entry: ClockifyTimeEntry) -> TimeEntry:

        description = entry.description
        if description:
            description += f" - {self._integration.project_name}"
        else:
            description = self._integration.project_name

        return TimeEntry(
            project_id=self._integration.integrated_project_id,
            description=description,
            started_at=entry.started,
            ended_at=entry.ended,
            duration=entry.duration or None,
            ref_id=entry.entry_id,
            ref_name="clockify"
        )

