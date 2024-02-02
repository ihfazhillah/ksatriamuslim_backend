import typing

from django.contrib import admin
from django.http import HttpRequest
from django.utils import timezone

from ksatria_muslim.invoice import models
from ksatria_muslim.invoice.cr import invoice_cr
from ksatria_muslim.invoice.integrations.clockify import ClockifyTimeEntry, ErrorResult
from ksatria_muslim.invoice.integrations.converters import Clockify as ClockifyConverter

@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "user")


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("client", "name", "rate", "currency", "user")


@admin.action(description="Lock selected entries")
def lock_selected_entries(modeladmin, request, queryset):
    now = timezone.now()
    queryset.update(locked=True, locked_at=now)
    modeladmin.message_user(request, "Your selected entries have been locked")


@admin.action(description="Unlock selected entries")
def unlock_selected_entries(modeladmin, request, queryset):
    queryset.update(locked=False, locked_at=None)
    modeladmin.message_user(request, "Your selected entries have been unlocked")


@admin.register(models.TimeEntry)
class TimeEntryModel(admin.ModelAdmin):
    list_display = ("project", "description", "started_at", "ended_at", "duration", "locked", "locked_at")
    ordering = ("-started_at",)
    actions = [lock_selected_entries, unlock_selected_entries]
    list_filter = ("locked", "project__client")


class ClockifyTimeEntryTransformer:
    def __init__(
        self,
        modeladmin: admin.ModelAdmin,
        request: HttpRequest,
        converter: ClockifyConverter,

    ):
        self._model_admin = modeladmin
        self._converter = converter
        self._request = request

    def __call__(self, entries: typing.List[ClockifyTimeEntry]):

        time_entries = [
            self._converter.time_entry_to_django(entry)
            for entry in entries
        ]
        created_object = models.TimeEntry.objects.bulk_create(time_entries, ignore_conflicts=True)
        self._model_admin.message_user(self._request, f"Added {len(created_object)} entries to database")


@admin.action(description="Get time entries from clockify")
def clockify_time_entries(modeladmin, request, queryset):

    for integration in queryset:
        clockify_holder = invoice_cr.clockify(integration.integrated_project.user_id)

        result = clockify_holder.client.time_entries(
            integration.workspace_id,
            integration.user_id
        )

        transformer = ClockifyTimeEntryTransformer(modeladmin, request, invoice_cr.converter(integration))
        transformed_result = result.transform(transformer)
        if isinstance(transformed_result, ErrorResult):
            modeladmin.message_user(request, transformed_result.error.message, level="error")


@admin.register(models.ClockifyIntegration)
class ClockifyIntegrationAdmin(admin.ModelAdmin):
    actions = [clockify_time_entries]


@admin.register(models.WebhookTest)
class WebhookTestAdmin(admin.ModelAdmin):
    list_display = ("body", "post", "headers", "created")


@admin.register(models.ClockifyWebhookIntegration)
class ClockifyWebhookIntegration(admin.ModelAdmin):
    list_display = ("name", "key", "event_key", "user")
