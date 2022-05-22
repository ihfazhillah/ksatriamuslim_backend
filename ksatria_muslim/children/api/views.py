from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from ksatria_muslim.children.api.serializers import ChildSerializer
from ksatria_muslim.children.models import Child


class ChildViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = ChildSerializer
    queryset = Child.objects.all()

    def get_queryset(self):
        return self.queryset.filter(parent=self.request.user)
