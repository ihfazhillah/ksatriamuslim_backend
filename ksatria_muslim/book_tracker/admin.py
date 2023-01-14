from django.contrib import admin

from ksatria_muslim.book_tracker.models import Book, Session, PageAccess


class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "page_count"]


admin.site.register(Book, BookAdmin)


class PageAccessInlineAdmin(admin.TabularInline):
    model = PageAccess
    fields = ("page_num", "done_at")


class BookSessionAdmin(admin.ModelAdmin):
    list_display = ["book", "child"]
    inlines = [PageAccessInlineAdmin]


admin.site.register(Session, BookSessionAdmin)
