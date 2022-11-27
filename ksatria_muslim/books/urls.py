from django.urls import path

from ksatria_muslim.books.views import book_image_gallery, book_text_page_csv

app_name = "books"
urlpatterns = [
    path("<pk>/pages-preview/", book_image_gallery, name="pages-preview"),
    path("<pk>/download-text/", book_text_page_csv, name="book-text-page-csv")
]
