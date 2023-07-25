from django.urls import path

from ksatria_muslim.sensors.views import water_control

app_name = "sensors"

urlpatterns = [
    path("", water_control, name="water-control")
]
