from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.contrib.admin import TabularInline
from django.utils.safestring import mark_safe

from ksatria_muslim.children_task.models import Task, TaskHistory, TikrarItem, Tikrar


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "image_display")

    def image_display(self, obj):
        if obj.image:
            return mark_safe(f"<img src='{obj.image.url}' width='100'/>")
        return ""

    image_display.short_description = "Image Preview"
    image_display.allow_tags = True


@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ("task", "child", "status", "modified")
    list_filter = ("status",)
    actions = ["mark_as_done"]

    @admin.action(description="Mark as done")
    def mark_as_done(self, request, qs):
        qs.update(status=TaskHistory.STATUS.finished)


class TikrarItemAdmin(SortableInlineAdminMixin, TabularInline):
    model = TikrarItem
    ordering = ["index"]


@admin.register(Tikrar)
class TikrarAdmin(admin.ModelAdmin):
    list_display = ["title", "max_tikrar", "version"]
    inlines = [TikrarItemAdmin]
