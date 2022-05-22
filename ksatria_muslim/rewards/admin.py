from django.contrib import admin

from ksatria_muslim.rewards.models import RewardHistory


@admin.register(RewardHistory)
class RewardAdmin(admin.ModelAdmin):
    list_display = ["child_name", "parent_name", "description", "reward_type", "count"]

    @admin.display(description="Child Name")
    def child_name(self, obj):
        return obj.child.name

    @admin.display(description="Parent")
    def parent_name(self, obj):
        return obj.child.parent.email

