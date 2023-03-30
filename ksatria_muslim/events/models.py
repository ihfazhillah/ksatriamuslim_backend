from django.contrib.auth import get_user_model
from django.db import models
from model_utils.models import TimeStampedModel


class EventOrganizer(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Event(TimeStampedModel):
    title = models.CharField(max_length=255)
    thumbnail = models.ImageField(upload_to="events/")
    youtube_link = models.TextField(null=True, blank=True)
    zoom_link = models.TextField(null=True, blank=True)

    presenter = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="event_presenters")
    submitter = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="submitted_events")

    organizer = models.ForeignKey(EventOrganizer, on_delete=models.CASCADE, related_name="events")

    started_at = models.DateTimeField()

    def __str__(self):
        return self.title
