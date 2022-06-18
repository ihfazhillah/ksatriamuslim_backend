from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PackagesConfig(AppConfig):
    name = "ksatria_muslim.packages"
    verbose_name = _("Packages")

    def ready(self):
        try:
            import ksatria_muslim.packages.signals  # noqa F401
        except ImportError:
            pass

