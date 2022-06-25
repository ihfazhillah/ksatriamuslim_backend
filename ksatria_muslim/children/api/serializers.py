from django.db import models
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from ksatria_muslim.children.models import Child, PhotoProfile
from ksatria_muslim.rewards.models import REWARD_TYPES


class PhotoProfileSerializer(ModelSerializer):
    class Meta:
        model = PhotoProfile
        fields = ["id", "photo"]


class ChildSerializer(ModelSerializer):
    picture = PhotoProfileSerializer(read_only=True)

    class Meta:
        model = Child
        fields = ["id", "name", "enable_read_to_me", "points", "stars", "parent_id", "picture"]
        read_only_fields = ["parent_id"]

    points = serializers.SerializerMethodField()
    def get_points(self, obj):
        return obj.rewards.filter(reward_type=REWARD_TYPES.Point).aggregate(models.Sum("count"))["count__sum"] or 0

    stars = serializers.SerializerMethodField()
    def get_stars(self, obj):
        return obj.rewards.filter(reward_type=REWARD_TYPES.Star).aggregate(models.Sum("count"))["count__sum"] or 0
