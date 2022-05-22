from django.db import models
from model_utils import choices
from model_utils.models import TimeStampedModel

from ksatria_muslim.children.models import Child

REWARD_TYPES = choices.Choices("Point", "Star")


class RewardHistory(TimeStampedModel):
    reward_type = models.CharField(
        max_length=255,
        choices=REWARD_TYPES,
        default=REWARD_TYPES.Point
    )
    description = models.TextField(null=True, blank=True)
    count = models.IntegerField(default=0)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="rewards")
