from django.contrib.auth import get_user_model

from ksatria_muslim.invoice.integrations.clockify import Client as ClockifyClient, ClockifyConfig
from ksatria_muslim.invoice.integrations.converters import Clockify as ClockifyConverter


def clockify_config_factory(user_id) -> ClockifyConfig:
    user = get_user_model().objects.get(pk=user_id)
    clockify_api_key = user.preferences["api_keys__clockify_api_key"]
    return ClockifyConfig(clockify_api_key)


class ClockifyHolder:
    def __init__(self, user_id):
        self._user_id = user_id

    @property
    def client(self):
        return ClockifyClient(clockify_config_factory(self._user_id))


class InvoiceCR:
    def clockify(self, user_id) -> ClockifyHolder:
        return ClockifyHolder(user_id)

    def converter(self, integration) -> ClockifyConverter:
        return ClockifyConverter(integration)


invoice_cr = InvoiceCR()
