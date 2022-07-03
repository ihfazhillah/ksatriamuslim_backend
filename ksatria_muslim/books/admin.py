from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline, StackedInline

from ksatria_muslim.books.models import Book, Page, BookReference, BookState, ChildBookReadingHistory


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


@admin.register(BookState)
class BookStateAdmin(ModelAdmin):
    list_display = ["child", "book", "is_gift_opened", "locked"]

    @admin.display(description="Child")
    def child(self, obj):
        return obj.child.name

    @admin.display(description="Book")
    def book(self, obj):
        return obj.book.title


@admin.register(ChildBookReadingHistory)
class ChildBookReadingHistoryAdmin(ModelAdmin):
    list_display = ["child", "book", "created"]
    @admin.display(description="Child")
    def child(self, obj):
        return obj.child.name

    @admin.display(description="Book")
    def book(self, obj):
        return obj.book.title

