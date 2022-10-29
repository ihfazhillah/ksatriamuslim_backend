from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from ksatria_muslim.books.models import Book


@login_required
def book_image_gallery(request, pk):
    instance = get_object_or_404(Book, pk=pk)
    return render(request, "books/image_gallery.html", {
        "instance": instance,
        "media_url": settings.MEDIA_URL,
        "sizes": [size[2] for size in settings.BOOK_IMAGE_SIZES]
    })
