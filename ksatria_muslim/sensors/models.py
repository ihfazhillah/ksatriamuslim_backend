from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel


class Board(models.Model):
    label = models.CharField(max_length=255, unique=True)
    token = models.CharField(default="", max_length=255)

    def __str__(self):
        return self.label


class Sensor(models.Model):
    CHOICES = Choices("Pir")

    label = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=CHOICES)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="sensors")

    def __str__(self):
        return self.label


class SensorLog(TimeStampedModel):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name="logs")
    message = models.TextField(null=True, blank=True)

    # used for track date from the device
    tracked_date = models.DateTimeField(null=True, blank=True)


class BoardLog(TimeStampedModel):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="logs")



class ImouAccount(TimeStampedModel):
    appid = models.TextField()
    appsecret = models.TextField()
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.label


class CCTVCamera(TimeStampedModel):
    label = models.CharField(max_length=255)
    camera_id = models.CharField(max_length=255)

    is_busy = models.BooleanField(default=False)
    stream_url = models.TextField(null=True, blank=True)

    account = models.ForeignKey(ImouAccount, on_delete=models.CASCADE)

    def __str__(self):
        return self.label
