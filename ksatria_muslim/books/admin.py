from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminBase
from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline, StackedInline
from django.urls import reverse
from django.utils.safestring import mark_safe

from ksatria_muslim.books.models import Book, Page, BookReference, BookState, ChildBookReadingHistory


class PageInline(SortableInlineAdminMixin, TabularInline):
    model = Page
    ordering = ["page"]


@admin.register(Book)
class BookAdmin(SortableAdminBase, ModelAdmin):
    list_display = ["title", "cover", "preview_pages", "download_text", "upload_audio_zip"]
    search_fields = ["title"]
    inlines = [PageInline]
    autocomplete_fields = ["reference"]
    readonly_fields = ["preview_pages", "download_text", "upload_audio_zip"]

    def preview_pages(self, obj):
        return mark_safe(
            f"<a href='{reverse('books:pages-preview', args=[obj.id])}' target='_blank'>Klik untuk melihat preview gambar halaman</a>"
        )

    def download_text(self, obj):
        return mark_safe(
            f"<a href='{reverse('books:book-text-page-csv', args=[obj.id])}' target='_blank'>Klik untuk mdownload text</a>"
        )

    def upload_audio_zip(self, obj):
        return mark_safe(
            f"<a href='{reverse('books:upload-audio-zip', args=[obj.id])}' target='_blank'>Klik untuk upload audio</a>"
        )


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
    list_display = ["child", "book", "created", "finished"]
    @admin.display(description="Child")
    def child(self, obj):
        return obj.child.name

    @admin.display(description="Book")
    def book(self, obj):
        return obj.book.title

