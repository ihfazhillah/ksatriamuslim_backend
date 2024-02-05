from django.utils import timezone

from ksatria_muslim.children_task.models import Task, TaskHistory


def get_children_tasks(child_id) -> list[TaskHistory]:
    tasks = Task.objects.filter(children__id=child_id)
    today_histories = [
        TaskHistory.objects.get_or_create(created=timezone.now(), task_id=task.id, child_id=child_id)
        for task in tasks
    ]
    return [instance for instance, created in today_histories]
