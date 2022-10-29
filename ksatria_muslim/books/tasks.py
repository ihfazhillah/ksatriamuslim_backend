from django.contrib.auth import get_user_model

from config import celery_app
from ksatria_muslim.books.models import Book
from ksatria_muslim.utils.book_image import is_arabic, process_page_image, stamp_book

User = get_user_model()


@celery_app.task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()


@celery_app.task()
def process_book(book_id):
    book = Book.objects.get(pk=book_id)
    for page in book.page_set.all():
        file_name = f"books/{book_id}/{page.page}"
        arabic = is_arabic(page.text)
        process_page_image(page.text, file_name, arabic)
        stamp_book(f"books/{book_id}/{page.page}/stamp")
