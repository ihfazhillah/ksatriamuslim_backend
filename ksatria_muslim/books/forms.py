import datetime
import json
import os
import zipfile

from django import forms
from django.core.files.storage import default_storage

from ksatria_muslim.books.book_storage import book_storage
from ksatria_muslim.books.models import Book


class UploadAudioForm(forms.Form):
    zip_file = forms.FileField()

    def __init__(self, *args, **kwargs):
        self.book: Book = kwargs.pop("book")
        super().__init__(*args, **kwargs)

    def clean_zip_file(self):
        data = self.cleaned_data["zip_file"]

        paths = []
        for page in self.book.page_set.all():
            fname = f"book_image_metadata/books/{self.book.id}/{page.page}-hdpi.json"
            paths.append((fname, page))

        rows = []
        for path, page in paths:
            f = default_storage.open(path)
            metadata = json.load(f)
            for index, item in enumerate(metadata.get("page_data", [])):
                # ganti kalau sudah mp3
                rows.append([f"{self.book.id}_{page.page}_{index}.mp3", item.get("text")])

        with zipfile.ZipFile(data, "r") as compressed:
            # first layer: validate extension
            for file in compressed.namelist():
                if not file.endswith("mp3") and not file.endswith("csv"):
                    raise forms.ValidationError("File ada yang bukan mp3")

            # second layer: validate file page
            for item, text in rows:
                if item not in compressed.namelist():
                    raise forms.ValidationError(f"File {item} tidak ditemukan di zipfile. text: {text}")

        return data

    def save(self):
        base_path = f"{self.book.id}/audio/"

        if not book_storage.exists(base_path):
            os.makedirs(
                book_storage.path(base_path),
                exist_ok=True
            )

        with zipfile.ZipFile(self.cleaned_data["zip_file"], "r") as compressed:
            compressed.extractall(book_storage.path(base_path))

        with open(book_storage.path(base_path + "timestamp"), "w") as timestamp:
            timestamp.write(str(datetime.datetime.now().timestamp()))

