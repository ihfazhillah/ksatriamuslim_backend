from django.db import models
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from ksatria_muslim.children.models import Child
from ksatria_muslim.children_task.models import TaskHistory
from ksatria_muslim.children_task.selectors import get_children_tasks


#############################
# children app related views
#############################


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
        # tasks = get_children_tasks(obj.id)
        today = timezone.localdate()
        tasks = TaskHistory.objects.filter(
            child_id=obj.id,
            task__active=True,
            task__days__contains=[today.isoweekday()],
            created__date=today
        ).order_by("task__scheduled_at", "task__title")
        if not tasks:
            return 0.0

        finished_task = [task for task in tasks if task.status in [TaskHistory.STATUS.finished, TaskHistory.STATUS.udzur]]
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

    time = "Belum Terjadwal"
    if history.task.scheduled_at:
        time =  history.task.scheduled_at.strftime("%H:%M")

    return {
        "id": history.id,
        "title": history.task.title,
        "status": history.status,
        "image": image_url,
        "udzur": history.udzur_reason,
        "time": time,
        "need_confirmation": history.task.need_verification,
        "created": history.created
    }


@api_view(["GET"])
def get_task_list(request, child_id):
    """
    Used in the children and parent detail
    """
    today = timezone.localdate()
    tasks = TaskHistory.objects.filter(
        child_id=child_id,
        task__active=True,
        task__days__contains=[today.isoweekday()],
        created__date=today
    ).order_by("task__scheduled_at", "task__title")
    return Response({"tasks": [serialize_task(task, request) for task in tasks]})


@api_view(["POST"])
def mark_as_finished(request):
    task_id = request.data.get("task_id")
    task = get_object_or_404(TaskHistory, id=task_id)

    if task.task.need_verification:
        photo = request.FILES.get("photo")
        if not photo:
            return Response({"message": "photo required"}, status=status.HTTP_400_BAD_REQUEST)

        task.photo = photo

    if task.task.need_verification:
        task.status = TaskHistory.STATUS.pending
    else:
        task.status = TaskHistory.STATUS.finished

    task.finished_at = timezone.now()

    task.save()
    return Response({"task": serialize_task(task, request)})



@api_view(["POST"])
def mark_as_udzur(request):
    task_id = request.data.get("task_id")
    udzur_reason = request.data.get("udzur_reason")
    task = get_object_or_404(TaskHistory, id=task_id)
    task.status = TaskHistory.STATUS.udzur
    task.udzur_reason = udzur_reason
    task.finished_at = timezone.now()
    task.save()
    return Response({"task": serialize_task(task, request)})


############################
# parent app related views
############################


@api_view(["POST"])
def update_status(request):
    task_id = request.data.get("task_id")
    task = get_object_or_404(TaskHistory, id=task_id)
    task.status = TaskHistory.STATUS.finished
    task.save()

    return Response({"task": serialize_task(task, request)})


@api_view(["GET"])
def today_parent_dashboard(request):
    today = timezone.localdate()

    to_review_count = TaskHistory.objects.filter(
        status=TaskHistory.STATUS.pending,
        child__parent=request.user
    ).count()

    # to optimize: mungkin bisa di check mana yang lebih cepat ->
    # get data dari tasks kemudian dihitung
    # atau get data dari anak dengan aggregate
    children = Child.objects.filter(parent=request.user).order_by("name").annotate(
        todo_count=models.Count("taskhistory", filter=models.Q(taskhistory__status=TaskHistory.STATUS.todo, created__date=today)),
        pending_count=models.Count("taskhistory",
                                filter=models.Q(taskhistory__status=TaskHistory.STATUS.pending, created__date=today)),
        udzur_count=models.Count("taskhistory",
                                   filter=models.Q(taskhistory__status=TaskHistory.STATUS.udzur,
                                                   created__date=today)),
        finished_count=models.Count("taskhistory",
                                 filter=models.Q(taskhistory__status=TaskHistory.STATUS.finished,
                                                 created__date=today)),
    )

    serialized_children = [
        {
            "id": child.id,
            "photo": request.build_absolute_uri(child.picture.photo.url),
            "name": child.name,
            "todo_count": child.todo_count,
            "udzur_count": child.udzur_count,
            "pending_count": child.pending_count,
            "finished_count": child.finished_count,
        }
        for child in children
    ]

    response_data = {
        "children": serialized_children,
        "to_review_count": to_review_count
    }

    return Response(response_data)


@api_view(["GET"])
def to_review_tasks_view(request):
    to_review_tasks = TaskHistory.objects.filter(
        status=TaskHistory.STATUS.pending,
        child__parent=request.user
    )

    serialized_tasks = [
        {
            "id": task.id,
            "verification_photo": request.build_absolute_uri(task.photo.url),
            "title": task.task.title,
            "photo": request.build_absolute_uri(task.task.image.url) if task.task.image else None,
            "submitted_at": task.updated
        }
        for task in to_review_tasks
    ]

    return Response({"tasks": serialized_tasks})



@api_view(["POST"])
def confirm(request):
    task_id = request.data.get("task_id")
    task = get_object_or_404(TaskHistory, id=task_id)

    selected_status = request.data.get("status")

    try:
        task.status = TaskHistory.STATUS[selected_status]
        task.save()
        return Response({"task": serialize_task(task, request)})
    except KeyError:
        return Response({"error": f"status {selected_status} not found"}, status=400)


@api_view(["POST"])
def reset(request):
    task_id = request.data.get("task_id")
    task = get_object_or_404(TaskHistory, id=task_id)
    task.status = TaskHistory.STATUS.todo
    task.save()

    return Response({"task": serialize_task(task, request)})
