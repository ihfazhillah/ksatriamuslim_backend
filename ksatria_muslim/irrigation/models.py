from django.db import models
from model_utils.models import TimeStampedModel


class Place(TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)

    def __str__(self):
        return self.title


class Controller(TimeStampedModel):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    label = models.CharField(max_length=255)
    token = models.TextField()

    def __str__(self):
        return self.label


class Device(TimeStampedModel):
    controller = models.ForeignKey(Controller, on_delete=models.CASCADE)
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.label


class DeviceHistory(TimeStampedModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    value_int = models.IntegerField()
    value_float = models.FloatField()


class Schedule(TimeStampedModel):
    index = models.IntegerField(default=0)
    time = models.TimeField()
    place = models.ForeignKey(Place, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.place} - {self.time}"


class RunHistory(TimeStampedModel):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, null=True)
