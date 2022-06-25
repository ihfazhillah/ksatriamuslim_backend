from django.contrib import admin
from django.utils.html import format_html

from ksatria_muslim.children.models import Child, PhotoProfile


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ("name", "parent_name", "display_photo")

    @admin.display(description="Parent")
    def parent_name(self, obj):
        return obj.parent.email

    @admin.display(description="Photo")
    def display_photo(self, obj):
        if not obj.picture:
            return "no picture"
        return format_html(f"<img src='{obj.picture.photo.url}' height='100' width='100'/>")


@admin.register(PhotoProfile)
class PhotoProfileAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "display_photo")

    @admin.display(description="Photo")
    def display_photo(self, obj):
        return format_html(f"<img src='{obj.photo.url}' height='100' width='100'/>")
