import uuid

from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel

from ksatria_muslim.children.models import Child


class Task(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=225)
    need_verification = models.BooleanField(default=False)
    children = models.ManyToManyField(Child)
    scheduled_at = models.TimeField(null=True, blank=True)

    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.title


class TaskHistory(TimeStampedModel):
    STATUS = Choices("todo", "pending", "finished")

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=STATUS, default=STATUS.todo)
