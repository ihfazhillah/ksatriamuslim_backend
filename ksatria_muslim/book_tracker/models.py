from django.db import models
from model_utils.models import TimeStampedModel

from ksatria_muslim.children.models import Child


class Book(TimeStampedModel):
    title = models.CharField(max_length=255)
    thumbnail = models.ImageField("book_tracker/books/")
    page_count = models.IntegerField()

    def __str__(self):
        return self.title


class Session(TimeStampedModel):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    child = models.ForeignKey(Child, on_delete=models.CASCADE)


class PageAccess(TimeStampedModel):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="pages")
    page_num = models.IntegerField()
    done_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["session", "page_num"]


def create_page_access(sender, instance: Session, created, **kwargs):
    if not created:
        return

    page_count = instance.book.page_count
    pages = list(range(1, page_count + 1))
    for page in pages:
        PageAccess.objects.create(session=instance, page_num=page)

