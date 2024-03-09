from django.db import models


class Document(models.Model):
    label = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    document_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.label} - {self.document_name}"


class Flowly(models.Model):
    key = models.TextField(db_index=True)
    value = models.TextField()
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ("key", "document_id")
