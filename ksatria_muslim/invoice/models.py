from django.contrib.auth import get_user_model
from django.db import models
from model_utils.models import TimeStampedModel


User = get_user_model()


class Client(TimeStampedModel):
    name = models.CharField(max_length=255)
    email = models.EmailField()

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # untuk sementara per client untuk konversian
    should_convert = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Project(TimeStampedModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5, default="USD")

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class TimeEntry(TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.TextField()

    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True, blank=True)

    # used if the time entry integrated from another application
    # such as clockify
    ref_id = models.CharField(max_length=255, null=True, blank=True)
    ref_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ("ref_id", "ref_name")
        verbose_name = "Time Entry"
        verbose_name_plural = "Time Entries"


# integrations
class ClockifyIntegration(TimeStampedModel):
    # from clockify fields
    workspace_id = models.CharField(max_length=255)
    workspace_name = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255)
    project_id = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255)

    integrated_project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("project_id", "integrated_project_id")

    def __str__(self):
        return f"{self.workspace_name} - {self.project_name} - {self.project_name}"


class ClockifyWebhookIntegration(TimeStampedModel):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_key = models.CharField(max_length=255)


# Used for webhook test, anything
class WebhookTest(TimeStampedModel):
    body = models.TextField(null=True, blank=True)
    post = models.TextField(null=True, blank=True)
    headers = models.TextField(null=True, blank=True)
