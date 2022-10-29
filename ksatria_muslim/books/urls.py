from django.urls import path

from ksatria_muslim.books.views import book_image_gallery

app_name = "books"
urlpatterns = [
    path("<pk>/pages-preview/", book_image_gallery, name="pages-preview")
]
