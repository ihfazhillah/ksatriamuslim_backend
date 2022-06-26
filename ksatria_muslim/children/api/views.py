from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ksatria_muslim.children.api.serializers import ChildSerializer, PhotoProfileSerializer
from ksatria_muslim.children.models import Child, PhotoProfile


class ChildViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = ChildSerializer
    queryset = Child.objects.all()

    def get_queryset(self):
        return self.queryset.filter(parent=self.request.user)

    @action(methods=["POST"], detail=True)
    def set_picture(self, request, pk, *args, **kwargs):
        obj = self.get_object()
        picture_id = request.data.get("picture_id")
        if picture_id:
            return Response({"message": "Bad Request"}, status=400)

        picture = get_object_or_404(PhotoProfile, pk=picture_id)
        obj.picture = picture
        obj.save()

        return Response(ChildSerializer(obj).data)


class PhotoProfileViewSet(ListModelMixin, GenericViewSet):
    serializer_class = PhotoProfileSerializer
    queryset = PhotoProfile.objects.all()
