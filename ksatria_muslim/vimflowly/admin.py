from django.contrib import admin
from django.contrib.admin import register

from ksatria_muslim.vimflowly.models import Flowly, Document


@register(Flowly)
class FlowlyAdmin(admin.ModelAdmin):
    list_display = ("document", "key", "value")
    list_filter = ("document",)
    search_fields = ("key", "value")


@register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("label", "document_name")
