from django.contrib.auth import get_user_model
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from .serializers import BookSerializer, BookDetailSerializer
from ..models import Book
from ...utils.pagination import KsatriaMuslimPagination

User = get_user_model()


class BookViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    pagination_class = KsatriaMuslimPagination

    def get_serializer_class(self):
        if self.action == "detail":
            return BookDetailSerializer
        return self.serializer_class
