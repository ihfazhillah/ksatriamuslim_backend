from django.contrib import admin
from django.contrib.admin import register

from .models import Board


@register(Board)
class BoardAdmin(admin.ModelAdmin):
    pass
