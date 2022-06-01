from django.contrib.auth import get_user_model
from rest_framework import serializers

from ksatria_muslim.books.models import Book, BookReference, Page

User = get_user_model()


class BookReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookReference
        fields = ["title", "author", "id"]


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = [
            "id",
            "page",
            "text",
            "audio"
        ]


class BookSerializer(serializers.ModelSerializer):
    reference = BookReferenceSerializer()
    # page_set = PageSerializer(many=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "cover",
            # "reference_text_ar",
            # "reference_text_id",
            # "reference",
            # "reference_note",
            "created",
            # "page_set"
        ]


class BookDetailSerializer(serializers.ModelSerializer):
    reference = BookReferenceSerializer()
    page_set = PageSerializer(many=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "cover",
            "reference_text_ar",
            "reference_text_id",
            "reference",
            "reference_note",
            "created",
            # "page_set"
        ]
