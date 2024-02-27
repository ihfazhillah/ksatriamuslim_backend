from django.contrib import admin
from django.contrib.admin import register

from ksatria_muslim.vimflowly.models import Flowly


@register(Flowly)
class FlowlyAdmin(admin.ModelAdmin):
    list_display = ("key", "value")
    pass
