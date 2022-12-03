from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.functional import LazyObject


class BookStorage(LazyObject):
    def _setup(self):
        self._wrapped = FileSystemStorage(
            settings.BOOK_STORAGE_MEDIA
        )


book_storage = BookStorage()
