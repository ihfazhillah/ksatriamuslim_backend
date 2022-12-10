import zipfile

import csv
import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.core.files.storage import default_storage

from ksatria_muslim.books.book_storage import book_storage
from ksatria_muslim.books.forms import UploadAudioForm
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
        for index, item in enumerate(metadata.get("page_data", [])):
            rows.append([pk, page.page, index, item.get("text")])

    response = HttpResponse(
        content_type="text/csv",
        headers={'Content-Disposition': f'attachment; filename="{instance.title}-texts.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(["book_id", "page_number", "index", "text"])
    writer.writerows(rows)
    return response


@login_required
def upload_audio_zip(request, pk):
    instance = get_object_or_404(Book, pk=pk)
    form = UploadAudioForm(
        book=instance,
        data=request.POST or None,
        files=request.FILES or None
    )
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("admin:books_book_changelist")

    context = {
        "form": form
    }
    return render(
        request,
        "books/upload-audio-zip.html",
        context
    )


def book_audio_zip(request, pk):
    token = request.GET.get("token")
    if not token:
        return HttpResponseForbidden()

    if not request.user.auth_token.key == token:
        return HttpResponseForbidden()

    instance = get_object_or_404(Book, pk=pk)
    base_path = f"{pk}/audio/"
    if not book_storage.exists(base_path):
        raise Http404("Audio not found.")

    timestamp = request.GET.get("timestamp", None)
    timestamp_file = f"{base_path}timestamp"
    if timestamp:
        # if found, check also if the given timestamp equals then
        # raise audio not found
        f = book_storage.open(timestamp_file, "r")
        if timestamp == f.read().strip():
            raise Http404("Audio same with in the local")
        f.close()

    _, files = book_storage.listdir(base_path)

    response = HttpResponse(
        content_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={instance.title}-audio.zip"
        }
    )

    with zipfile.ZipFile(response, "w") as compressor:
        for file in files:
            compressor.write(book_storage.path(f"{base_path}{file}"), arcname=file)

    return response
