from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline, StackedInline

from ksatria_muslim.books.models import Book, Page, BookReference


class PageInline(SortableInlineAdminMixin, TabularInline):
    model = Page
    ordering = ["page"]


@admin.register(Book)
class BookAdmin(ModelAdmin):
    list_display = ["title", "cover"]
    search_fields = ["title"]
    inlines = [PageInline]
    autocomplete_fields = ["reference"]


@admin.register(BookReference)
class BookReferenceAdmin(ModelAdmin):
    search_fields = ["title", "author"]
