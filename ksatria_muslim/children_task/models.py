import uuid

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
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
    active = models.BooleanField(default=True)

    days = ArrayField(models.IntegerField(validators=[MaxValueValidator(7), MinValueValidator(1)]), default=list)

    def __str__(self):
        return self.title


class TaskHistory(TimeStampedModel):
    STATUS = Choices("todo", "pending", "finished", "udzur")

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=STATUS, default=STATUS.todo)
    udzur_reason = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to="task_history/", null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)


