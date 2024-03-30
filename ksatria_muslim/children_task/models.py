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
    active = models.BooleanField(default=True)

    TYPES = Choices("yesno", "need_verification", "tikrar")
    type = models.CharField(max_length=255, default=TYPES.yesno, choices=TYPES)
    detail = models.JSONField(default=dict)

    def __str__(self):
        return self.title


class TaskHistory(TimeStampedModel):
    STATUS = Choices("todo", "pending", "finished")

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=STATUS, default=STATUS.todo)


class Tikrar(TimeStampedModel):
    """
    Bank data untuk tikrar
    """
    title = models.CharField(max_length=255)
    max_tikrar = models.IntegerField(default=3)

    # should be increased every file generated
    version = models.IntegerField(default=0)
    generated_file = models.FileField(null=True, blank=True, upload_to="tikrar/")


class TikrarItem(TimeStampedModel):
    tikrar = models.ForeignKey(Tikrar, on_delete=models.CASCADE, related_name="items")
    index = models.IntegerField(default=0)
    text = models.TextField()
    audio = models.FileField(upload_to="tikrar-audio/")

    class Meta:
        ordering = ["index"]
