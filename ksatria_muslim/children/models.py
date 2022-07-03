from django.contrib.auth import get_user_model
from django.db import models
from model_utils.models import TimeStampedModel


User = get_user_model()


class Child(TimeStampedModel):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    enable_read_to_me = models.BooleanField(default=False)
    picture = models.ForeignKey("PhotoProfile", null=True, blank=True, on_delete=models.SET_NULL)
    default_package = models.ForeignKey("packages.Package", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class PhotoProfile(TimeStampedModel):
    photo = models.ImageField(upload_to="child_profiles/")
    title = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
