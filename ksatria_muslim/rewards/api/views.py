from django.db import models
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ksatria_muslim.children.models import Child
from ksatria_muslim.packages.api.serializers import BuyPackageBodySerializer
from ksatria_muslim.packages.models import ChildPackage
from ksatria_muslim.rewards.models import RewardHistory, REWARD_TYPES


class RewardHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardHistory
        fields = [
            "reward_type",
            "description",
            "count",
            "child"
        ]


class RewardSubtractSerializer(serializers.Serializer):
    count = serializers.IntegerField(max_value=-1)
    message = serializers.CharField()
    child_id = serializers.PrimaryKeyRelatedField(queryset=Child.objects.all())


class RewardHistoryViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = RewardHistorySerializer
    queryset = RewardHistory.objects.all()

    @action(methods=["POST"], detail=False)
    def request_access(self, request, pk=None):
        serializer = RewardSubtractSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data["child_id"].parent != request.user:
            return Response({"permissible": False, "message": "not_parent"})

        rewards = RewardHistory.objects.filter(
            child=serializer.validated_data["child_id"],
            reward_type=REWARD_TYPES.Point
        )
        current_rewards = rewards.aggregate(current=models.Sum("count"))["current"] or 0

        if current_rewards < abs(serializer.validated_data["count"]):
            return Response({"permissible": False, "message": "no_coin"})

        RewardHistory.objects.create(
            child=serializer.validated_data["child_id"],
            count=serializer.validated_data["count"],
            description=serializer.validated_data["message"]
        )

        return Response({"permissible": True, "message": "can_access"})

    @action(["POST"], detail=False)
    def buy_package(self, request):
        serializer = BuyPackageBodySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        child = serializer.validated_data["child"]
        package = serializer.validated_data["package"]

        if child.parent != request.user:
            return Response({"permissible": False, "message": "not_parent"})

        current_rewards = self._get_current_reward(child)

        child_package = ChildPackage.objects.filter(
            child=child,
            package=package,
            is_exhausted=False
        ).first()

        if not child_package and current_rewards < package.price:
            return Response({
                "permissible": False,
                "coin_remaining": current_rewards,
                "duration_remaining": 0,
                "message": "no_coin"
            })

        if not child_package and current_rewards >= package.price:
            # pembelian
            RewardHistory.objects.create(
                child=child,
                count=-package.price,
                description=f"Buy Package {package.title}"
            )

            # package
            child_package = ChildPackage.objects.create(
                child=child,
                package=package
            )

        remaining = child_package.remaining
        coin = self._get_current_reward(child)
        return Response(
            {"permissible": True, "duration_remaining": remaining, "coin_remaining": coin}
        )

    @staticmethod
    def _get_current_reward(child):
        rewards = RewardHistory.objects.filter(
            child=child,
            reward_type=REWARD_TYPES.Point
        )
        current_rewards = rewards.aggregate(current=models.Sum("count"))["current"] or 0
        return current_rewards



