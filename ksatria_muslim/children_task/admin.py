from django.contrib import admin

from ksatria_muslim.children_task.models import Task, TaskHistory


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass


@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = ("task", "child", "status", "modified")
    list_filter = ("status",)
    actions = ["mark_as_done"]

    @admin.action(description="Mark as done")
    def mark_as_done(self, qs):
        qs.update(status=TaskHistory.STATUS.finished)
