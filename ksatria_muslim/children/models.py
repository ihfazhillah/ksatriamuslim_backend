from django.contrib.auth import get_user_model
from django.db import models
from model_utils.models import TimeStampedModel


User = get_user_model()


class Child(TimeStampedModel):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    enable_read_to_me = models.BooleanField(default=False)
