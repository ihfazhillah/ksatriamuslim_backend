from django.db import models
from django.utils import timezone
from model_utils.models import TimeStampedModel

from ksatria_muslim.children.models import Child


class BookReference(TimeStampedModel):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Book(TimeStampedModel):
    title = models.CharField(max_length=255)
    cover = models.ImageField(upload_to="cover_books/")

    # we not used the reference text for the old books
    reference_text_ar = models.TextField(null=True, blank=True)
    reference_text_id = models.TextField(null=True, blank=True)
    reference = models.ForeignKey(BookReference, on_delete=models.SET_NULL, null=True, blank=True)
    reference_note = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title


def page_audio(instance, filename):
    return f"audiobook/{instance.book_id}/{instance.page}"


class Page(TimeStampedModel):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    page = models.IntegerField(db_index=True, default=0)
    text = models.TextField()
    audio = models.FileField(upload_to=page_audio, null=True, blank=True)

    class Meta:
        ordering = ["page"]


class BookState(TimeStampedModel):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    is_gift_opened = models.BooleanField(default=False)

    class Meta:
        unique_together = ["book", "child"]

    @property
    def locked(self):
        latest_history = ChildBookReadingHistory.objects.filter(
            child=self.child, book=self.book
        ).order_by("-created")[:]
        if not latest_history:
            return False

        days_delta = (timezone.now() - latest_history[0].created).days
        multiples_of_ten = len(latest_history) / 10 == 0

        return multiples_of_ten and days_delta <= 3


class ChildBookReadingHistory(TimeStampedModel):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
