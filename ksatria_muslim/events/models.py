from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from model_utils import Choices


class Event(models.Model):
    DATE_TYPES = Choices("hijri", "masehi")

    date_type = models.CharField(max_length=20, choices=DATE_TYPES)

    date = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(31)])
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    image = models.ImageField(upload_to="events/")

    def __str__(self):
        return self.title


