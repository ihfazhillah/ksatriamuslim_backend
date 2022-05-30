from django.contrib.auth import get_user_model
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from .serializers import BookSerializer
from ..models import Book
from ...utils.pagination import KsatriaMuslimPagination

User = get_user_model()


class BookViewSet(ListModelMixin, GenericViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    pagination_class = KsatriaMuslimPagination
