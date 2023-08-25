from django.apps import AppConfig


class IrrigationAppConfig(AppConfig):
    name = "ksatria_muslim.irrigation"

    def ready(self) -> None:
        import ksatria_muslim.irrigation.mqtt
