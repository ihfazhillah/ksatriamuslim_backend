from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "ksatria_muslim.books"
    verbose_name = _("Books")

    def ready(self):
        try:
            import ksatria_muslim.books.signals  # noqa F401
        except ImportError:
            pass
