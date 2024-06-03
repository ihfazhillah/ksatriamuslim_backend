from django.contrib import admin
from django.utils.safestring import mark_safe

from ksatria_muslim.children_task.models import Task, TaskHistory


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("image_display", "title", "scheduled_at", "days", "children_display")
    list_filter = ("days", "children")
    ordering = ("scheduled_at", "title")
    list_display_links = ("title",)

    def image_display(self, obj):
        if obj.image:
            return mark_safe(f"<img src='{obj.image.url}' width='100'/>")
        return ""

    image_display.short_description = "Image Preview"
    image_display.allow_tags = True

    def children_display(self, obj):
        data = [
            child.name for child in obj.children.all()
        ]
        return ", ".join(data)
    children_display.short_description = "Children"


@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ("task", "child", "status", "modified")
    list_filter = ("status",)
    actions = ["mark_as_done"]

    @admin.action(description="Mark as done")
    def mark_as_done(self, request, qs):
        qs.update(status=TaskHistory.STATUS.finished)

