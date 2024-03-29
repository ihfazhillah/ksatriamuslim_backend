from django.contrib import admin
from django.contrib.admin import register
from django.utils import timezone

from ksatria_muslim.irrigation.models import Place, Controller, Device, DeviceHistory, Schedule, RunHistory


class ScheduleAdmin(admin.TabularInline):
    model = Schedule


@register(Place)
class PlaceAdmin(admin.ModelAdmin):
    inlines = [ScheduleAdmin]


@register(Controller)
class ControllerAdmin(admin.ModelAdmin):
    list_display = ("place", "label")


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("label", "latest_value", "latest_update")

    @admin.display
    def latest_value(self, obj):
        histories = DeviceHistory.objects.filter(device=obj).order_by("-created").first()
        if not histories:
            return ""
        if histories.value_int:
            return histories.value_int
        if histories.value_float:
            return histories.value_float

    @admin.display
    def latest_update(self, obj):
        histories = DeviceHistory.objects.filter(device=obj).order_by("-created").first()
        if not histories:
            return ""
        if histories.created:
            return timezone.localtime(histories.created)



@admin.register(RunHistory)
class RunHistoryAdmin(admin.ModelAdmin):
    list_display = ("schedule", "created")
    list_filter = ("schedule",)
