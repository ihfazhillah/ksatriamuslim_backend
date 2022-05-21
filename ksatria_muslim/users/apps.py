from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "ksatria_muslim.users"
    verbose_name = _("Users")

    def ready(self):
        try:
            import ksatria_muslim.users.signals  # noqa F401
        except ImportError:
            pass
