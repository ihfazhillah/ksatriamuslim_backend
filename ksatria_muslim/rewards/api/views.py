from rest_framework import serializers
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from ksatria_muslim.rewards.models import RewardHistory


class RewardHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardHistory
        fields = [
            "reward_type",
            "description",
            "count",
            "child"
        ]


class RewardHistoryViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = RewardHistorySerializer
    queryset = RewardHistory.objects.all()
