from django.db import models
from model_utils import Choices


class Event(models.Model):
    DATE_TYPES = Choices("hijri", "masehi")

    date_type = models.CharField(max_length=20, choices=DATE_TYPES)

    date = models.IntegerField(null=True, blank=True)
    month = models.IntegerField()

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    image = models.ImageField(upload_to="events/")

    def __str__(self):
        return self.title


