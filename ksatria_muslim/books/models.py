from django.db import models
from model_utils.models import TimeStampedModel


class BookReference(TimeStampedModel):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)


class Book(TimeStampedModel):
    title = models.CharField(max_length=255)
    cover = models.ImageField(upload_to="cover_books/")
    reference_text_ar = models.TextField()
    reference_text_id = models.TextField()
    reference = models.ForeignKey(BookReference, on_delete=models.SET_NULL, null=True)


def page_audio(instance, filename):
    return f"audiobook/{instance.book_id}/{instance.page}"


class Page(TimeStampedModel):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    page = models.IntegerField()
    text = models.TextField()
    audio = models.FileField(upload_to=page_audio, null=True, blank=True)
