from django.contrib.auth import get_user_model
from rest_framework.decorators import action, api_view
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import BookSerializer, BookDetailSerializer, BookStateSerializer
from ..models import Book, BookState, ChildBookReadingHistory
from ..tasks import process_book
from ...utils.pagination import KsatriaMuslimPagination

User = get_user_model()


class BookViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all().order_by("-id")
    pagination_class = KsatriaMuslimPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookDetailSerializer
        return self.serializer_class

    def get_queryset(self):
        return self.queryset.order_by("-id")

    @action(detail=True, methods=["POST"])
    def update_state(self, request, pk=None):
        book = self.get_object()

        child_id = request.data.get("child_id")
        if not child_id:
            return Response({"error": "no child id supplied"}, status=400)

        gift_opened = request.data.get("gift_opened", False)

        BookState.objects.update_or_create(
            book=book,
            child_id=child_id,
            defaults={"is_gift_opened": gift_opened}
        )

        return Response({"status": "ok"})

    @action(detail=True, methods=["POST"])
    def log(self, request, pk=None):
        book = self.get_object()

        child_id = request.data.get("child_id")
        if not child_id:
            return Response({"error": "no child id supplied"}, status=400)

        ChildBookReadingHistory.objects.create(
            book=book,
            child_id=child_id
        )

        return Response({"status": "ok"})


class BookStateViewSet(ListModelMixin, GenericViewSet):
    serializer_class = BookStateSerializer
    queryset = BookState.objects.all()

    def get_queryset(self):
        book_ids = self.request.query_params.getlist("books_id")
        child_id = self.request.query_params.get("child_id")
        qs = BookState.objects.all()

        if book_ids:
            qs = qs.filter(book_id__in=book_ids)

        if child_id:
            qs = qs.filter(child_id=child_id)

        return qs


@api_view(["GET"])
def force_generate_images(request):
    for book in Book.objects.all():
        process_book.delay(book.id)
    return Response({"status": "ok"})
