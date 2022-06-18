from django.db import models
from model_utils.models import TimeStampedModel

from ksatria_muslim.children.models import Child


class Package(TimeStampedModel):
    title = models.CharField(max_length=255, unique=True)
    price = models.PositiveIntegerField()

    length = models.PositiveIntegerField()  # length on minutes

    def __str__(self):
        return self.title


class ChildPackage(TimeStampedModel):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="children")
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="purchased_packages")
    is_exhausted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.child_id} - {self.package_id}"


class PackageUsage(TimeStampedModel):
    child_package = models.ForeignKey(ChildPackage, on_delete=models.CASCADE, related_name="usages")
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)

    @property
    def duration(self):
        if not self.finished_at:
            return 0
        return (self.finished_at - self.started_at).total_seconds()

    def __str__(self):
        return f"{self.duration} - {self.child_package_id}"
