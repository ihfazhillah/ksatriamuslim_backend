from django.dispatch import receiver
from dmqtt.signals import topic, connect, regex

from ksatria_muslim.irrigation.models import Device, DeviceHistory, Place, Schedule, RunHistory, Controller


@receiver(connect)
def on_connect(sender, **kwargs):
    sender.subscribe("#")

@topic("/some/test", as_json=False)
def handle_test(sender, topic, msg, **kwargs):
    print(sender)
    print(topic)
    print(msg.payload)
    # print(**kwargs)


@regex("^controller/(?P<token>[a-zA-Z0-9]+)/(?P<device>\d+)$", as_json=False)
def handle_battery(match, msg, **kwargs):
    device = match.groupdict()
    value = msg.payload.decode("utf-8")
    try:
        device = Device.objects.get(controller__token=device["token"], pk=device["device"])
        DeviceHistory.objects.create(device=device, value_float=float(value))
    except Device.DoesNotExist:
        print("device not found")


@regex("^place/(?P<id>\d+)/controller/(?P<token>[a-zA-Z0-9]+)/feeding$", as_json=False)
def handle_feeding_schedule(match, msg, **kwargs):
    device = match.groupdict()

    try:
        Controller.objects.get(token=device["token"])
    except Controller.DoesNotExist:
        return

    value = msg.payload.decode("utf-8")
    try:
        place = Place.objects.get(pk=device["id"])
        try:
            schedule = Schedule.objects.get(place=place, index=int(value))
        except Schedule.DoesNotExist:
            schedule = None
        except ValueError:
            schedule = None

        RunHistory.objects.create(schedule=schedule)

    except Place.DoesNotExist:
        print("place not found")
