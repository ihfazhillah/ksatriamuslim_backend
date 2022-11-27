import csv
import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.core.files.storage import default_storage

from ksatria_muslim.books.models import Book


@login_required
def book_image_gallery(request, pk):
    instance = get_object_or_404(Book, pk=pk)
    return render(request, "books/image_gallery.html", {
        "instance": instance,
        "media_url": settings.MEDIA_URL,
        "sizes": [size[2] for size in settings.BOOK_IMAGE_SIZES]
    })


@login_required
def book_text_page_csv(request, pk):
    instance: Book = get_object_or_404(Book, pk=pk)
    paths = []
    for page in instance.page_set.all():
        fname = f"book_image_metadata/books/{pk}/{page.page}-hdpi.json"
        paths.append((fname, page))

    rows = []
    for path, page in paths:
        f = default_storage.open(path)
        metadata = json.load(f)
        for item in metadata.get("page_data", []):
            rows.append([pk, page.page, item.get("text")])

    response = HttpResponse(
        content_type="text/csv",
        headers={'Content-Disposition': f'attachment; filename="{instance.title}-texts.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(["book_id", "page_number", "text"])
    writer.writerows(rows)
    return response
