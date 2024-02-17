from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from ksatria_muslim.children.models import Child
from ksatria_muslim.children_task.models import TaskHistory
from ksatria_muslim.children_task.selectors import get_children_tasks


class ChildSerializer(serializers.ModelSerializer):
    avatarUrl = serializers.SerializerMethodField("get_avatarUrl")
    progress = serializers.SerializerMethodField("get_progress")

    class Meta:
        model = Child
        fields = ("id", "name", "avatarUrl", "progress")

    def get_avatarUrl(self, obj: Child):
        request = self.context.get("request")

        url = obj.picture.photo.url

        if request:
            return request.build_absolute_uri(url)

        return url

    def get_progress(self, obj: Child):
        tasks = get_children_tasks(obj.id)
        if not tasks:
            return 0.0

        finished_task = [task for task in tasks if task.status == TaskHistory.STATUS.finished]
        return len(finished_task) / len(tasks)



@api_view(["GET"])
def get_children(request):
    children = Child.objects.filter(parent=request.user)
    serializer = ChildSerializer(children, many=True, context={"request": request})
    return Response({"profiles": serializer.data})


def serialize_task(history: TaskHistory, request=None):

    image_url = ""
    if history.task.image:
        image_url = history.task.image.url
        if request:
            image_url = request.build_absolute_uri(image_url)

    return {
        "id": history.id,
        "title": history.task.title,
        "status": history.status,
        "image": image_url
    }


@api_view(["GET"])
def get_task_list(request, child_id):
    tasks = get_children_tasks(child_id)
    tasks = sorted(tasks, key=lambda history: history.modified, reverse=True)
    return Response({"tasks": [serialize_task(task, request) for task in tasks]})


@api_view(["POST"])
def mark_as_finished(request):
    task_id = request.data.get("task_id")
    task = get_object_or_404(TaskHistory, id=task_id)

    if task.task.need_verification:
        task.status = TaskHistory.STATUS.pending
    else:
        task.status = TaskHistory.STATUS.finished

    task.save()
    return Response({"task": serialize_task(task, request)})


@api_view(["POST"])
def confirm(request):
    task_id = request.data.get("task_id")
    task = get_object_or_404(TaskHistory, id=task_id)
    task.status = TaskHistory.STATUS.finished
    task.save()

    return Response({"task": serialize_task(task, request)})
